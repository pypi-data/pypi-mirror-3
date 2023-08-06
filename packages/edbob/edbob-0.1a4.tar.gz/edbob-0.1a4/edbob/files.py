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
``edbob.files`` -- Files & Folders
"""


import os
import os.path
import shutil
import tempfile


__all__ = ['change_newlines', 'count_lines', 'temp_path']


def change_newlines(path, newline):
    """
    Rewrites the file at ``path``, changing its newline character(s) to that of
    ``newline``.
    """

    root, ext = os.path.splitext(path)
    temp_path = temp_path(suffix='.' + ext)
    infile = open(path, 'rUb')
    outfile = open(temp_path, 'wb')
    for line in infile:
        line = line.rstrip('\r\n')
        outfile.write(line + newline)
    infile.close()
    outfile.close()
    os.remove(path)
    shutil.move(temp_path, path)


def count_lines(path):
    """
    Convenience function to count the number of lines in a text file.  Some
    attempt is made to ensure cross-platform compatibility.
    """

    f = open(path, 'rb')
    lines = f.read().count('\n') + 1
    f.close()
    return lines


def temp_path(suffix='.tmp', prefix='edbob.'):
    """
    Convenience function to return a temporary file path.  The arguments'
    meanings are the same as for ``tempfile.mkstemp()``.
    """

    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    os.remove(path)
    return path
