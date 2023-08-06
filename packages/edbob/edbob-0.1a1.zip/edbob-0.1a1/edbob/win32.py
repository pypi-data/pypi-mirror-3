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
``edbob.win32`` -- Stuff for Microsoft Windows
"""

import sys
if sys.platform == 'win32': # docs should build for everyone
    import win32api
    import win32con
    import pywintypes
    import win32file
    import winerror


def RegDeleteTree(key, subkey):
    """
    This is a clone of ``win32api.RegDeleteTree()``, since that apparently
    requires Vista or later.
    """

    def delete_contents(key):
        subkeys = []
        for name, reserved, class_, mtime in win32api.RegEnumKeyEx(key):
            subkeys.append(name)
        for subkey_name in subkeys:
            subkey = win32api.RegOpenKeyEx(key, subkey_name, 0, win32con.KEY_ALL_ACCESS)
            delete_contents(subkey)
            win32api.RegCloseKey(subkey)
            win32api.RegDeleteKey(key, subkey_name)
        values = []
        i = 0
        while True:
            try:
                name, value, type_ = win32api.RegEnumValue(key, i)
            except pywintypes.error, e:
                if e[0] == winerror.ERROR_NO_MORE_ITEMS:
                    break
            values.append(name)
            i += 1
        for value in values:
            win32api.RegDeleteValue(key, value)

    orig_key = key
    try:
        key = win32api.RegOpenKeyEx(orig_key, subkey, 0, win32con.KEY_ALL_ACCESS)
    except pywintypes.error, e:
        if e[0] != winerror.ERROR_FILE_NOT_FOUND:
            raise
    else:
        delete_contents(key)
        win32api.RegCloseKey(key)
    try:
        win32api.RegDeleteKey(orig_key, subkey)
    except pywintypes.error, e:
        if e[0] == winerror.ERROR_FILE_NOT_FOUND:
            pass


def file_is_free(path):
    """
    Returns boolean indicating whether or not the file located at ``path`` is
    currently tied up in any way by another process.
    """

    # This code was borrowed from Nikita Nemkin:
    # http://stackoverflow.com/a/2848266

    handle = None
    try:
        handle = win32file.CreateFile(
            path,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None)
        return True
    except pywintypes.error, e:
        if e[0] == winerror.ERROR_SHARING_VIOLATION:
            return False
        raise
    finally:
        if handle:
            win32file.CloseHandle(handle)
