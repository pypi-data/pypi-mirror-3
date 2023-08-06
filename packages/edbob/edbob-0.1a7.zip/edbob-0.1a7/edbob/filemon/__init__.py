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
``edbob.filemon`` -- File Monitoring Service
"""

import edbob
from edbob.exceptions import ConfigError


class MonitorProfile(object):
    """
    This is a simple profile class, used to represent configuration of the file
    monitor service.
    """

    def __init__(self, key):
        self.key = key
        self.dirs = eval(edbob.config.require('edbob.filemon', '%s.dirs' % key))
        if not self.dirs:
            raise ConfigError('edbob.filemon', '%s.dirs' % key)
        self.actions = eval(edbob.config.require('edbob.filemon', '%s.actions' % key))
        if not self.actions:
            raise ConfigError('edbob.filemon', '%s.actions' % key)
