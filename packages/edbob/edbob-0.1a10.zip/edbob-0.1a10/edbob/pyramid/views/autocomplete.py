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
``edbob.pyramid.views.autocomplete`` -- Autocomplete View
"""

from pyramid.renderers import render_to_response

from edbob.pyramid import Session
from edbob.pyramid.forms.formalchemy import AutocompleteFieldRenderer
from edbob.util import requires_impl


__all__ = ['AutocompleteView']


class AutocompleteView(object):

    route = None
    url = None

    def __init__(self, request):
        self.request = request

    @property
    @requires_impl(is_property=True)
    def mapped_class(self):
        raise NotImplementedError

    @property
    @requires_impl(is_property=True)
    def fieldname(self):
        raise NotImplementedError

    @classmethod
    def get_route(cls):
        if not cls.route:
            name = cls.mapped_class.__name__.lower()
            cls.route = '%ss.autocomplete' % name
        return cls.route

    def filter_query(self, q):
        return q

    def make_query(self, query):
        q = Session.query(self.mapped_class)
        q = self.filter_query(q)
        q = q.filter(getattr(self.mapped_class, self.fieldname).ilike('%%%s%%' % query))
        q = q.order_by(getattr(self.mapped_class, self.fieldname))
        return q

    def query(self, query):
        return self.make_query(query)

    def __call__(self):
        query = self.request.params['query']
        objs = self.query(query).all()
        data = dict(
            query=query,
            suggestions=[getattr(x, self.fieldname) for x in objs],
            data=[x.uuid for x in objs],
            )
        response = render_to_response('json', data, request=self.request)
        response.headers['Content-Type'] = 'application/json'
        return response

    @classmethod
    def add_route(cls, config):
        """
        Add 'autocomplete' route to the config object.
        """

        name = cls.mapped_class.__name__.lower()
        route = cls.get_route()
        url = cls.url or '/%ss/autocomplete' % name

        config.add_route(route, url)
        config.add_view(cls, route_name=route, http_cache=0)

    @classmethod
    def renderer(cls, request):
        return AutocompleteFieldRenderer(request.route_url(cls.get_route()),
                                         (cls.mapped_class, cls.fieldname))
