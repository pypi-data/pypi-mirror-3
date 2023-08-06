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

# Much of the Windows monitoring code below was borrowed from Tim Golden:
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html

import sys
import os.path
import threading
import logging
import subprocess

import edbob
from edbob.exceptions import ConfigError

if sys.platform == 'win32':
    import win32file
    import win32con


FILE_LIST_DIRECTORY = 0x0001

ACTION_CREATE           = 1
ACTION_DELETE           = 2
ACTION_UPDATE           = 3
ACTION_RENAME_TO        = 4
ACTION_RENAME_FROM      = 5

log = logging.getLogger(__name__)


def exec_server_command(command):
    """
    Executes ``command`` against the file monitor Windows service, i.e. one of:

    * ``'install'``
    * ``'start'``
    * ``'stop'``
    * ``'remove'``
    """
    server_path = os.path.join(os.path.dirname(__file__), 'filemon_server.py')
    subprocess.call([sys.executable, server_path, command])


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


def monitor_win32(path, include_subdirs=False):
    """
    This is the workhorse of file monitoring on the Windows platform.  It is a
    generator function which yields a ``(file_type, file_path, action)`` tuple
    whenever changes occur in the monitored folder.  ``file_type`` will be one
    of:
    
    * ``'file'``
    * ``'folder'``
    * ``'<deleted>'``

    ``file_path`` will be the path to the changed object; and ``action`` will
    be one of:

    * ``ACTION_CREATE``
    * ``ACTION_DELETE``
    * ``ACTION_UPDATE``
    * ``ACTION_RENAME_TO``
    * ``ACTION_RENAME_FROM``

    (The above are "constants" importable from ``edbob.filemon``.)

    This function leverages the ``ReadDirectoryChangesW()`` Windows API
    function.  This is nice because the OS now reports changes to us so that we
    needn't poll to find them.

    However ``ReadDirectoryChangesW()`` is a blocking call, so in practice this
    means that if, say, you're using this function in a python shell, you will
    not be able to stop the process with a keyboard interrupt.  (Actually you
    sort of can, as long as you send the interrupt and then perform some file
    operation which will trigger the monitoring function to return.)

    Fortunately the primary need for this function is by the Windows service,
    which is of course "disconnected" from the user's desktop and never really
    needs to close under normal circumstances.
    """
    hDir = win32file.CreateFile(
        path,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)

    while True:
        results = win32file.ReadDirectoryChangesW (
            hDir,
            1024,
            include_subdirs,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | 
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None)

        for action, fn in results:
            fpath = os.path.join(path, fn)
            if not os.path.exists(fpath):
                ftype = "<deleted>"
            elif os.path.isdir(fpath):
                ftype = "folder"
            else:
                ftype = "file"
            yield ftype, fpath, action


class WatcherWin32(threading.Thread):
    """
    A ``threading.Thread`` subclass which is responsible for monitoring a
    particular folder (on Windows platforms).
    """

    def __init__(self, key, path, queue, include_subdirs=False, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.setDaemon(1)
        self.key = key
        self.path = path
        self.queue = queue
        self.include_subdirs = include_subdirs
        self.start()

    def run(self):
        for result in monitor_win32(self.path,
                                    include_subdirs=self.include_subdirs):
            self.queue.put((self.key,) + result)
