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
``edbob.pyramid.views.grids.core`` -- Core Grid View
"""

from edbob.pyramid import grids
from edbob.pyramid.views.core import View


__all__ = ['GridView']


class GridView(View):

    route_name = None
    route_url = None
    renderer = None
    permission = None
    checkboxes = False
    clickable = False
    partial_only = False

    def update_grid_kwargs(self, kwargs):
        kwargs.setdefault('checkboxes', self.checkboxes)
        kwargs.setdefault('clickable', self.clickable)
        kwargs.setdefault('partial_only', self.partial_only)

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.Grid(self.request, **kwargs)

    def grid(self):
        return self.make_grid()

    def __call__(self):
        grid = self.grid()
        return grids.util.render_grid(grid)

    @classmethod
    def add_route(cls, config, route_name=None, route_url=None, renderer=None, permission=None):
        route_name = route_name or cls.route_name
        route_url = route_url or cls.route_url
        renderer = renderer or cls.renderer
        permission = permission or cls.permission
        config.add_route(route_name, route_url)
        config.add_view(cls, route_name=route_name, renderer=renderer,
                        permission=permission, http_cache=0)
