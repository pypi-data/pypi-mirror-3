#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  edbob -- Pythonic Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of edbob.
#
#  edbob is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  edbob is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with edbob.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``edbob.time`` -- Date & Time Utilities
"""

import datetime
import pytz
import logging


__all__ = ['local_time', 'set_timezone', 'utc_time']

log = logging.getLogger(__name__)

timezone = None


def init(config):
    """
    Initializes the time framework.  Currently this only sets the local
    timezone according to config.
    """

    tz = config.get('edbob.time', 'timezone')
    if tz:
        set_timezone(tz)
        log.debug("Timezone set to '%s'" % tz)
    else:
        log.warning("No timezone configured; falling back to US/Central")
        set_timezone('US/Central')
    

def local_time(timestamp=None):
    """
    Tries to return a "localized" version of ``timestamp``, which should be a
    UTC-based ``datetime.datetime`` instance.

    If a local timezone has been configured, then
    ``datetime.datetime.utcnow()`` will be called to obtain a value for
    ``timestamp`` if one is not specified.  Then ``timestamp`` will be modified
    in such a way that its ``tzinfo`` member contains the local timezone, but
    the effective UTC value for the timestamp remains accurate.

    If a local timezone has *not* been configured, then
    ``datetime.datetime.now()`` will be called instead to obtain the value
    should none be specified.  ``timestamp`` will be returned unchanged.
    """

    if timezone:
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()
        timestamp = pytz.utc.localize(timestamp)
        return timestamp.astimezone(timezone)

    if timestamp is None:
        timestamp = datetime.datetime.now()
    return timestamp


def set_timezone(tz):
    """
    Sets edbob's notion of the "local" timezone.  ``tz`` should be an Olson
    name.

    .. highlight:: ini

    You usually don't need to call this yourself, since it's called by
    :func:`edbob.init()` whenever the config file includes a timezone (but
    only as long as ``edbob.time`` is configured to be initialized)::

       [edbob]
       init = edbob.time

       [edbob.time]
       timezone = US/Central
    """

    global timezone

    if tz is None:
        timezone = None
    else:
        timezone = pytz.timezone(tz)


def utc_time(timestamp=None):
    """
    Returns a timestamp whose ``tzinfo`` member is set to the UTC timezone.

    If ``timestamp`` is not provided, then ``datetime.datetime.utcnow()`` will
    be called to obtain the value.
    """

    if timestamp is None:
        timestamp = datetime.datetime.utcnow()
    return pytz.utc.localize(timestamp)
