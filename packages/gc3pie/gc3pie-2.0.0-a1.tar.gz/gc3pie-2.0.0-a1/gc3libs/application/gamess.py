#! /usr/bin/env python
#
"""
Specialized support for computational jobs running GAMESS-US.
"""
# Copyright (C) 2009-2012 GC3, University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
__docformat__ = 'reStructuredText'
__version__ = '2.0.0-a1 version (SVN $Revision: 2593 $)'


import gc3libs
import gc3libs.application
import gc3libs.application.apppot
import gc3libs.exceptions
import os
import os.path
import re


class GamessApplication(gc3libs.Application):
    """
    Specialized `Application` object to submit computational jobs running GAMESS-US.

    The only required parameter for construction is the input file
    name; subsequent positional arguments are additional input files,
    that are added to the `Application.inputs` list, but not otherwise
    treated specially.

    The `verno` parameter is used to request a specific version of
    GAMESS-US; if the default value ``None`` is used, the default
    version of GAMESS-US at the executing site is run.

    Any other keyword parameter that is valid in the `Application`
    class can be used here as well, with the exception of `input` and
    `output`.  Note that a GAMESS-US job is *always* submitted with
    `join = True`, therefore any `stderr` setting is ignored.
    """
    def __init__(self, inp_file_path, *other_input_files, **kw):
        input_file_name = os.path.basename(inp_file_path)
        input_file_name_sans = os.path.splitext(input_file_name)[0]
        output_file_name = input_file_name_sans + '.dat'
        # add defaults to `kw` if not already present
        kw.setdefault('stdout', input_file_name_sans + '.out')
        kw.setdefault('tags', list())
        self.verno = kw.get('verno', None)
        if self.verno is not None:
            kw['tags'].append("APPS/CHEM/GAMESS-%s" % self.verno)
        else:
            # no VERNO specified
            kw['tags'].append("APPS/CHEM/GAMESS")
        # `rungms` has a fixed structure for positional arguments:
        # INPUT VERNO NCPUS; if one of them is to be omitted,
        # we use the empty string instead.
        arguments = [
            input_file_name,
            str(kw.get('verno') or ""),
            str(kw.get('requested_cores') or "")
            ]
        if 'extbas' in kw:
           other_input_files += kw['extbas']
           arguments.extend(['--extbas', os.path.basename(kw['extbas'])])
        #set job name
        kw['job_name'] = input_file_name_sans
        # build generic `Application` obj
        gc3libs.Application.__init__(self,
                                     executable = "/$RUNGMS", # XXX: should be: "rungms",
                                     arguments = arguments,
                                     inputs = [ inp_file_path ] + list(other_input_files),
                                     outputs = [ output_file_name ],
                                     join = True,
                                     # needed by `ggamess`
                                     inp_file_path = inp_file_path,
                                     **kw)

    _termination_re = re.compile(r'EXECUTION \s+ OF \s+ GAMESS \s+ TERMINATED \s+-?(?P<gamess_outcome>NORMALLY|ABNORMALLY)-?'
                                 r'|ddikick.x: .+ (exited|quit) \s+ (?P<ddikick_outcome>gracefully|unexpectedly)', re.X)

    def terminated(self):
        """
        Append to log the termination status line as extracted from
        the GAMESS '.out' file.

        The job exit code `.execution.exitcode` is (re)set according
        to the following table:

        =====================  ===============================================
        Exit code              Meaning
        =====================  ===============================================
        0                      the output file contains the string \
                               ``EXECUTION OF GAMESS TERMINATED normally``
        1                      the output file contains the string \
                               ``EXECUTION OF GAMESS TERMINATED -ABNORMALLY-``
        2                      the output file contains the string \
                               ``ddikick exited unexpectedly``
        70 (`os.EX_SOFTWARE`)  the output file cannot be read or \
                               does not match any of the above patterns
        =====================  ===============================================

        """
        gc3libs.log.debug("Running GamessApplication post-processing hook...")
        output_dir = self.output_dir
        output_filename = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(self.inp_file_path))[0] + '.out')
        if not os.path.exists(output_filename):
            # no output file, override exit code if it indicates success
            if self.execution.exitcode == os.EX_OK:
                self.execution.exitcode = os.EX_SOFTWARE
        else:
            # output file exists, start with pessimistic default and
            # override if we find a "success" keyword
            self.execution.exitcode = os.EX_SOFTWARE # internal software error
            gc3libs.log.debug("Trying to read GAMESS termination status"
                              " off output file '%s' ..." % output_filename)
            output_file = open(output_filename, 'r')
            for line in output_file:
                match = self._termination_re.search(line)
                if match:
                    if match.group('gamess_outcome'):
                        self.execution.info = line.strip().capitalize()
                        if match.group('gamess_outcome') == 'ABNORMALLY':
                            self.execution.exitcode = 1
                        elif match.group('gamess_outcome') == 'NORMALLY':
                            self.execution.exitcode = 0
                        break
                    elif match.group('ddikick_outcome'):
                        self.execution.info = line.strip().capitalize()
                        if match.group('ddikick_outcome') == 'unexpectedly':
                            self.execution.exitcode = 2
                        # If the GAMESS execution terminated normally, this would
                        # have been catched by the test above; otherwise we risk here
                        # setting the exitcode to EX_OK even if GAMESS didn't run at
                        # all, but `ddikick` does not flag it as an error. (Not sure
                        # this can actually happen, but better err on the safe side.)
                        #elif match.group('ddikick_outcome') == 'gracefully':
                        #    gc3libs.log.info('Setting exit code to 0')
                        #    self.execution.exitcode = 0
                        break
                    else:
                        raise AssertionError(
                            "Input line '%s' matched,"
                            " but neither group 'gamess_outcome'"
                            " nor 'ddikick_outcome' did!")
            output_file.close()


    def qgms(self, resource, **kw):
        """
        Return the *argv*-vector for invoking `qgms` to run GAMESS-US
        with the parameters embedded in this object.
        """
        try:
            qgms_argv = [ os.path.join(resource.gamess_location, 'qgms') ]
        except AttributeError:
            raise gc3libs.exceptions.ConfigurationError(
                "Missing configuration parameter `gamess_location` on resource '%s'.",
                resource.name)

        if self.requested_walltime:
            # XXX: should this be an error instead?
            gc3libs.log.warning(
                "Requested %d hours of wall-clock time,"
                " but setting running time limits is not supported by the `qgms` script."
                " Ignoring request, GAMESS job will be submitted with unspecified running time.",
                self.requested_walltime)
        if self.requested_memory:
            # XXX: should this be an error instead?
            gc3libs.log.warning(
                "Requested %d Gigabytes of memory per core,"
                " but setting memory limits is not supported by the `qgms` script."
                " Ignoring request, GAMESS job will be submitted with unspecified memory requirements.",
                self.requested_memory)
        if self.requested_cores:
            qgms_argv += ['-n', '%d' % self.requested_cores]
        # silently ignore `self.job_name`: `qgms` will set it to a default

        # finally, add the input files
        qgms_argv += [ os.path.basename(r) for r in self.inputs.values() ]
        return (qgms_argv, [])

    # XXX: Assumes `qgms` is the correct way to run GAMESS on *any*
    # batch system, which it's not... see Issue 3
    qsub_sge = qgms
    qsub_pbs = qgms
    bsub = qgms


    def cmdline(self, resource, **kw):
        raise NotImplementedError(
            "There is currently no way of running GAMESS directly from the command-line."
            " GAMESS invocation requires too many deployment-specific parameters"
            " to make a generic invocation script possible.")



class GamessAppPotApplication(GamessApplication,
                              gc3libs.application.apppot.AppPotApplication):
    """
    Specialized `AppPotApplication` object to submit computational
    jobs running GAMESS-US.

    This class makes no check or guarantee that a GAMESS-US executable
    will be available in the executing AppPot instance: the
    `apppot_img` and `apppot_tag` keyword arguments can be used to
    select the AppPot system image to run this application; see the
    `AppPotApplication`:class: for information.

    The `__init__` construction interface is compatible with the one
    used in `GamessApplication`:class:. The only required parameter for
    construction is the input file name; any other argument names an
    additional input file, that is added to the `Application.inputs`
    list, but not otherwise treated specially.

    Any other keyword parameter that is valid in the `Application`
    class can be used here as well, with the exception of `input` and
    `output`.  Note that a GAMESS-US job is *always* submitted with
    `join = True`, therefore any `stderr` setting is ignored.
    """
    def __init__(self, inp_file_path, *other_input_files, **kw):
        input_file_name = os.path.basename(inp_file_path)
        input_file_name_sans = os.path.splitext(input_file_name)[0]
        output_file_name = input_file_name_sans + '.dat'
        # add defaults to `kw` if not already present
        kw.setdefault('stdout', input_file_name_sans + '.out')
        kw.setdefault('application_tag', "gamess")
        kw.setdefault('tags', list())
        kw['tags'].insert(0, "APPS/CHEM/GAMESS-APPPOT-0.11.11.08")
        if kw.has_key('extbas') and kw['extbas'] is not None:
            other_input_files += kw['extbas']
            arguments.extend(['--extbas', os.path.basename(extbas)])
        # set job name
        kw['job_name'] = input_file_name_sans
        # init superclass
        gc3libs.application.apppot.AppPotApplication.__init__(
            self,
            executable = "localgms",
            # `rungms` has a fixed structure for positional arguments:
            # INPUT VERNO NCPUS; if one of them is to be omitted,
            # we cannot use the empty string instead because `apppot-start`
            # cannot detect it from the kernel command line, so we have to
            # hard-code default values here...
            arguments = [
                input_file_name,
                str(kw.get('verno') or "00"),
                str(kw.get('requested_cores') or "")
                ],
            inputs = [ inp_file_path ] + list(other_input_files),
            outputs = [ output_file_name ],
            join = True,
            # needed by `ggamess`
            inp_file_path = inp_file_path,
            **kw)

    # XXX: need to override the `qgms`, `qsub` and `cmdline`
    # definitions made by `GamessApplication`.  This can go away
    # once `GamessApplication` has a sane interface for running
    # GAMESS (see Issue 3 on the web site).
    bsub = gc3libs.Application.bsub
    cmdline = gc3libs.Application.cmdline
    qsub_pbs = gc3libs.Application.qsub_pbs
    qsub_sge = gc3libs.Application.qsub_sge



## main: run tests

if "__main__" == __name__:
    import doctest
    doctest.testmod(name="gamess",
                    optionflags=doctest.NORMALIZE_WHITESPACE)


