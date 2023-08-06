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
``edbob.pyramid.views.grid`` -- Base Grid View
"""

from edbob.pyramid import filters
from edbob.pyramid import forms
from edbob.pyramid import grids
from edbob.pyramid import Session
from edbob.util import requires_impl


__all__ = ['GridView']


class GridView(object):

    @property
    @requires_impl(is_property=True)
    def mapped_class(self):
        raise NotImplementedError

    @property
    @requires_impl(is_property=True)
    def route_name(self):
        raise NotImplementedError

    @property
    @requires_impl(is_property=True)
    def route_prefix(self):
        raise NotImplementedError

    def __init__(self, request):
        self.request = request

    def join_map(self):
        return {}

    def make_filter_map(self, **kwargs):
        return filters.get_filter_map(self.mapped_class, **kwargs)

    def filter_map(self):
        return self.make_filter_map()

    def make_search_config(self, fmap, **kwargs):
        return filters.get_search_config(self.route_name, self.request, fmap,
                                         **kwargs)

    def search_config(self, fmap):
        return self.make_search_config(fmap)

    def make_search_form(self, config, **labels):
        return filters.get_search_form(config, **labels)

    def search_form(self, config):
        return self.make_search_form(config)

    def make_sort_map(self, *args, **kwargs):
        return grids.get_sort_map(self.mapped_class, names=args or None, **kwargs)

    def sort_map(self):
        return self.make_sort_map()

    def make_grid_config(self, search, fmap, deletable=True, **kwargs):
        return grids.get_grid_config(
            self.route_name, self.request, search,
            filter_map=fmap, deletable=deletable, **kwargs)

    def grid_config(self, search, fmap):
        return self.make_grid_config(search, fmap)

    def filter_query(self, q):
        return q

    def make_query(self, config, jmap=None):
        if jmap is None:
            jmap = self.join_map()
        smap = self.sort_map()
        q = Session.query(self.mapped_class)
        q = self.filter_query(q)
        q = filters.filter_query(q, config, jmap)
        q = grids.sort_query(q, config, smap, jmap)
        return q

    def query(self, config):
        return self.make_query(config)

    def make_grid(self, data, config, gridurl=None, objurl=None, delurl=None):
        if not gridurl:
            gridurl = self.request.route_url(self.route_name)
        if not objurl:
            objurl = '%s.edit' % self.route_prefix
        if not delurl:
            delurl = '%s.delete' % self.route_prefix
        g = forms.AlchemyGrid(
            self.mapped_class, data, config,
            gridurl=gridurl, objurl=objurl, delurl=delurl)
        return g

    def grid(self, data, config):
        g = self.make_grid(data, config)
        g.configure(readonly=True)
        return g

    def __call__(self):
        """
        View callable method.
        """

        fmap = self.filter_map()
        config = self.search_config(fmap)
        search = self.search_form(config)
        config = self.grid_config(search, fmap)
        grid = grids.get_pager(self.query, config)

        g = self.grid(grid, config)
        grid = g.render(class_='clickable %s' % self.mapped_class.__name__)
        return grids.render_grid(self.request, grid, search)

    @classmethod
    def add_route(cls, config, route_name, url_prefix, template_prefix=None, permission=None):
        if not template_prefix:
            template_prefix = url_prefix
        if not permission:
            permission = route_name
        config.add_route(route_name, url_prefix)
        config.add_view(cls, route_name=route_name, renderer='%s/index.mako' % template_prefix,
                        permission=permission, http_cache=0)
