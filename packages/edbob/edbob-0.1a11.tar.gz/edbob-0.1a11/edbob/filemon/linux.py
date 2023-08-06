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
``edbob.filemon.linux`` -- File Monitor for Linux
"""

import sys
import os
import os.path
import signal
import pyinotify

import edbob
from edbob.filemon import MonitorProfile


class EventHandler(pyinotify.ProcessEvent):
    """
    Event processor for file monitor daemon.
    """

    def my_init(self, actions=[], **kwargs):
        self.actions = actions

    def process_IN_CREATE(self, event):
        self.perform_actions(event.pathname)

    def process_IN_MOVED_TO(self, event):
        self.perform_actions(event.pathname)

    def perform_actions(self, path):
        for action in self.actions:
            if isinstance(action, tuple):
                func = action[0]
                args = action[1:]
            else:
                func = action
                args = []
            func = edbob.load_spec(func)
            func(path, *args)


def get_pid_path():
    """
    Returns the path to the PID file for the file monitor daemon.
    """

    basename = os.path.basename(sys.argv[0])
    return '/tmp/%s_filemon.pid' % basename


def start_daemon():
    """
    Starts the file monitor daemon.
    """

    pid_path = get_pid_path()
    if os.path.exists(pid_path):
        print "File monitor is already running"
        return

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)

    monitored = {}
    keys = edbob.config.require('edbob.filemon', 'monitored')
    keys = keys.split(',')
    for key in keys:
        key = key.strip()
        monitored[key] = MonitorProfile(key)

    mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO
    for profile in monitored.itervalues():
        for path in profile.dirs:
            wm.add_watch(path, mask, proc_fun=EventHandler(actions=profile.actions))

    notifier.loop(daemonize=True, pid_file=pid_path)


def stop_daemon():
    """
    Stops the file monitor daemon.
    """

    pid_path = get_pid_path()
    if not os.path.exists(pid_path):
        print "File monitor is not running"
        return

    f = open(pid_path)
    pid = f.read().strip()
    f.close()
    if not pid.isdigit():
        print "Hm, found bogus PID:", pid
        return

    os.kill(int(pid), signal.SIGKILL)
    os.remove(pid_path)
