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
``edbob.pyramid.subscribers`` -- Subscribers
"""

from pyramid import threadlocal
from pyramid.security import authenticated_userid

import edbob
from edbob.db.auth import has_permission
from edbob.pyramid import helpers
from edbob.pyramid import Session


def before_render(event):
    """
    Adds goodies to the global template renderer context:

       * ``h``
       * ``url``
       * ``edbob``
    """

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['url'] = request.route_url
    renderer_globals['edbob'] = edbob


def context_found(event):
    """
    This hook attaches the :class:`edbob.User` instance for the currently
    logged-in user to the request (if there is one) as ``request.user``.

    Also adds a ``has_perm()`` function to the request, which is a shortcut for
    :func:`edbob.db.auth.has_permission()`.
    """

    def has_perm_func(request):
        def has_perm(perm):
            if not request.user:
                return False
            return has_permission(request.user, perm)
        return has_perm

    request = event.request
    request.has_perm = has_perm_func(request)

    request.user = None
    uuid = authenticated_userid(request)
    if uuid:
        request.user = Session.query(edbob.User).get(uuid)


def includeme(config):
    config.add_subscriber('edbob.pyramid.subscribers:before_render',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('edbob.pyramid.subscribers.context_found',
                          'pyramid.events.ContextFound')
