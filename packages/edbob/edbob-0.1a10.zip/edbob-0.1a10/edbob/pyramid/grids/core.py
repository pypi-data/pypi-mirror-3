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
``edbob.pyramid.grids.core`` -- Core Grid Classes
"""

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from webhelpers.html import literal
from webhelpers.html.builder import format_attrs

from pyramid.renderers import render

import edbob


__all__ = ['Grid']


class Grid(edbob.Object):

    hoverable = True
    clickable = False
    checkboxes = False
    deletable = False
    partial_only = False
    row_route_name = None
    row_route_kwargs = None

    def __init__(self, request, **kwargs):
        kwargs.setdefault('fields', OrderedDict())
        kwargs.setdefault('extra_columns', [])
        super(Grid, self).__init__(**kwargs)
        self.request = request

    def add_column(self, name, label, callback):
        self.extra_columns.append(
            edbob.Object(name=name, label=label, callback=callback))

    def column_header(self, field):
        return literal('<th field="%s">%s</th>' % (field.name, field.label))

    def div_class(self):
        if self.clickable:
            return 'grid clickable'
        if self.hoverable:
            return 'grid hoverable'
        return 'grid'

    def _div_attrs(self):
        attrs = {'class_':'grid', 'url':self.request.current_route_url()}
        if self.clickable:
            attrs['class_'] = 'grid clickable'
        elif self.hoverable:
            attrs['class_'] = 'grid hoverable'
        return attrs

    def div_attrs(self):
        return format_attrs(**self._div_attrs())

    def iter_fields(self):
        return self.fields.itervalues()

    def iter_rows(self):
        raise NotImplementedError

    def render(self, template='/grids/grid.mako', **kwargs):
        kwargs.setdefault('grid', self)
        return render(template, kwargs)

    def render_field(self, field):
        raise NotImplementedError

    def row_attrs(self, row, i):
        attrs = {'class_': 'odd' if i % 2 else 'even'}
        return attrs

    def get_row_attrs(self, row, i):
        attrs = self.row_attrs(row, i)
        if self.row_route_name:
            kwargs = {}
            if self.row_route_kwargs:
                if callable(self.row_route_kwargs):
                    kwargs = self.row_route_kwargs(row)
                else:
                    kwargs = self.row_route_kwargs
            attrs['url'] = self.request.route_url(self.row_route_name, **kwargs)
        return format_attrs(**attrs)
