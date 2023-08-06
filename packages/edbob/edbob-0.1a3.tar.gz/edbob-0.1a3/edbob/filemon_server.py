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
``edbob.filemon_server`` -- File Monitoring Service for Windows
"""

import os.path
import socket
import time
import Queue

import edbob
from edbob.win32 import file_is_free
from edbob.filemon import (MonitorProfile, WatcherWin32,
                             ACTION_CREATE, ACTION_UPDATE)

import sys
if sys.platform == 'win32': # docs should build for everyone
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import win32api


class FileMonitorService(win32serviceutil.ServiceFramework):
    """
    Implements edbob's file monitor Windows service.
    """

    _svc_name_ = "Edbob File Monitor"
    _svc_display_name_ = "Edbob : File Monitoring Service"
    _svc_description_ = ("Monitors one or more folders for incoming files, "
                         "and performs configured actions as new files arrive.")

    appname = 'edbob'

    def __init__(self, *args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        edbob.init(self.appname)
        self.main()

    def main(self):
        self.monitored = {}
        monitored = edbob.config.require('edbob.filemon', 'monitored')
        monitored = monitored.split(',')
        for m in monitored:
            m = m.strip()
            self.monitored[m] = MonitorProfile(m)
        queue = Queue.Queue()

        for key in self.monitored:
            for d in self.monitored[key].dirs:
                WatcherWin32(key, d, queue)

        while not self.stop_requested:
            try:
                key, ftype, fpath, action = queue.get_nowait()
            except Queue.Empty:
                pass
            else:
                if ftype == 'file' and action in (
                    ACTION_CREATE, ACTION_UPDATE):
                    self.do_actions(key, fpath)
            win32api.SleepEx(250, True)

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_, ''))

    def do_actions(self, key, path):
        if not os.path.exists(path):
            return
        while not file_is_free(path):
            # TODO: Add configurable timeout so long-open files can't hijack
            # our prcessing.
            time.sleep(0.25)
        for action in self.monitored[key].actions:
            if isinstance(action, tuple):
                func = action[0]
                args = action[1:]
            else:
                func = action
                args = []
            func = edbob.load_spec(func)
            func(path, *args)

    
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FileMonitorService)
