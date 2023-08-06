#! /usr/bin/env python
"""
Simple-minded scheduling for GC3Libs.
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


import sys

import gc3libs
from gc3libs.exceptions import *


def _compatible_resources(lrms_list, application):
    """
    Return list of resources in `lrms_list` that match the requirements
    in `application`.
    """
    _selected_lrms_list = []
    for lrms in lrms_list:
        assert(lrms is not None), \
            "Scheduler._compatible_resources(): expected `LRMS` object, got `None` instead."
        gc3libs.log.debug(
            "Checking resource '%s' for compatibility with application requirements"
            % lrms.name)
        # if architecture is specified, check that it matches the resource one
        if (application.requested_architecture is not None
            and application.requested_architecture not in lrms.architecture):
            gc3libs.log.info("Rejecting resource '%s': requested a different architecture (%s) than what resource provides (%s)"
                             % (lrms.name, application.requested_architecture,
                                str.join(', ', [str(arch) for arch in lrms.architecture ])))
            continue
        # check that Application requirements are within resource limits
        if (application.requested_cores is not None
            and int(application.requested_cores) > int(lrms.max_cores_per_job or sys.maxint)):
            gc3libs.log.info("Rejecting resource '%s': requested more cores (%d) that resource provides (%d)"
                             % (lrms.name, application.requested_cores, lrms.max_cores_per_job))
            continue
        if (application.requested_memory is not None
            and int(application.requested_memory) > int(lrms.max_memory_per_core or sys.maxint)):
            gc3libs.log.info("Rejecting resource '%s': requested more memory per core (%d GB) that resource provides (%d GB)"
                             % (lrms.name, application.requested_memory, lrms.max_memory_per_core))
            continue
        if (application.requested_walltime is not None
            and int(application.requested_walltime) > int(lrms.max_walltime or sys.maxint)):
            gc3libs.log.info("Rejecting resource '%s': requested a longer duration (%d s) that resource provides (%s h)"
                             % (lrms.name, application.requested_walltime, lrms.max_walltime))
            continue
        # XXX: Obsolete
        # Now LRMS.validate_data() will check is a given LRMS can handle the data protocol specified
        # if upload to remote site requested, check that the backend supports it
        # if (application.output_base_url is not None
        #     and lrms.type not in [
        #         gc3libs.Default.ARC0_LRMS,
        #         gc3libs.Default.ARC1_LRMS,
        #         ]):
        #     gc3libs.log.info("Rejecting resource '%s': no support for non-local output files."
        #                      % lrms.name)
        #     continue
        if not lrms.validate_data(application.inputs.keys()) or not lrms.validate_data(application.outputs.values()):
            gc3libs.log.info("Rejecting resource '%s': input/output data protocol not supported."
                             % lrms.name)
            continue

        _selected_lrms_list.append(lrms)

    return _selected_lrms_list


def _cmp_resources(a,b):
    """
    Compare resources `a` and `b` and return -1,0,1 accordingly
    (see doc for the Python standard function `cmp`).

    Computational resource `a` is preferred over `b` if it has less
    queued jobs from the same user; failing that, if it has more free
    slots; failing that, if it has less queued jobs (in total);
    finally, should all preceding parameters compare equal, `a` is
    preferred over `b` if it has less running jobs from the same user.
    """
    a_ = (a.user_queued, -a.free_slots,
          a.queued, a.user_run)
    b_ = (b.user_queued, -b.free_slots,
          b.queued, b.user_run)
    return cmp(a_, b_)


def do_brokering(lrms_list, application):
    assert (application is not None), \
        "Scheduler.do_brokering(): expected valid `Application` object, got `None` instead."
    rs = _compatible_resources(lrms_list, application)
    if len(rs) <= 1:
        # shortcut: no brokering to do, just use the only resource we've got
        return rs
    # get up-to-date resource status
    updated_resources = []
    for r in rs:
        try:
            # in-place update of resource status
            gc3libs.log.debug("Trying to update status of resource '%s' ..."
                              % r.name)
            r.get_resource_status()
            updated_resources.append(r)
        except Exception, x:
            # ignore errors in update, assume resource has a problem
            # and just drop it
            gc3libs.log.error("Cannot update status of resource '%s', dropping it."
                              " See log file for details."
                              % r.name)
            gc3libs.log.debug("Got error from get_resource_status(): %s: %s",
                              x.__class__.__name__, x.args, exc_info=True)
    return sorted(updated_resources, cmp=_cmp_resources)

## main: run tests

if "__main__" == __name__:
    import doctest
    doctest.testmod(name="__init__",
                    optionflags=doctest.NORMALIZE_WHITESPACE)
