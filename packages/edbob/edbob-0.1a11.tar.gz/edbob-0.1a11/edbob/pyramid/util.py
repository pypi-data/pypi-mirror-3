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
``edbob.pyramid.util`` -- Utilities
"""


def get_referer(request, default=None):
    """
    Returns a "referer" URL.
    """

    if request.params.get('referer'):
        return request.params['referer']
    if request.session.get('referer'):
        return request.session.pop('referer')
    referer = request.referer
    if not referer or referer == request.current_route_url():
        if default:
            referer = default
        else:
            referer = request.route_url('home')
    return referer
