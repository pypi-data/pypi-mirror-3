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
``edbob.initialization`` -- Initialization Framework
"""

import os
import logging

import edbob
from edbob.configuration import (
    AppConfigParser,
    default_system_paths,
    default_user_paths,
    )


__all__ = ['init']

log = logging.getLogger(__name__)


def init(appname='edbob', *args, **kwargs):
    """
    Initializes the edbob framework, typically by first reading some config
    file(s) to determine which interfaces to engage.  This must normally be
    called prior to doing anything really useful, as it is responsible for
    extending the live API in-place.

    The meaning of ``args`` is as follows:

    If ``args`` is empty, the ``EDBOB_CONFIG`` environment variable is first
    consulted.  If it is nonempty, then its value is split according to
    ``os.pathsep`` and the resulting sequence is passed to
    ``edbob.config.read()``.

    If both ``args`` and ``EDBOB_CONFIG`` are empty, the "standard" locations
    are assumed, and the results of calling both
    :func:`edbob.configuration.default_system_paths()` and
    :func:`edbob.configuration.default_user_paths()` are passed on to
    ``edbob.config.read()``.

    Any other values in ``args`` will be passed directly to
    ``edbob.config.read()`` and so will be interpreted there.  Basically they
    are assumed to be either strings, or sequences of strings, which represent
    paths to various config files, each being read in the order in which it
    appears within ``args``.  (Configuration is thereby cascaded such that the
    file read last will override those before it.)
    """

    config = AppConfigParser(appname)
 
    if args:
        config_paths = list(args)
    elif os.environ.get('EDBOB_CONFIG'):
        config_paths = os.environ['EDBOB_CONFIG'].split(os.pathsep)
    else:
        config_paths = default_system_paths(appname) + default_user_paths(appname)

    shell = bool(kwargs.get('shell'))
    for paths in config_paths:
        config.read(paths, recurse=not shell)
    config.configure_logging()

    default_modules = 'edbob.time'
    modules = config.get('edbob', 'init', default=default_modules)
    if modules:
        for name in modules.split(','):
            name = name.strip()
            module = __import__(name, globals(), locals(), fromlist=['init'])
            getattr(module, 'init')(config)
            # config.inited.append(name)

    # config.inited.append('edbob')
    edbob.graft(edbob, locals(), 'config')
    edbob.inited = True
