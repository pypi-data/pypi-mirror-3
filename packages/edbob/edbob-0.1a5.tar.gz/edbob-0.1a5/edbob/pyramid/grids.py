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
``edbob.pyramid.grids`` -- Grid Tables
"""

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute

from pyramid.renderers import render
from pyramid.response import Response
from webhelpers import paginate
from webhelpers.html import literal
from webhelpers.html.builder import format_attrs

import edbob
from edbob.pyramid.filters import SearchFormRenderer
from edbob.util import prettify


class BasicGrid(edbob.Object):
    """
    Basic grid class for those times when SQLAlchemy is not needed.
    """

    def __init__(self, columns, rows, config, url, sortable=True, deletable=False, **kwargs):
        edbob.Object.__init__(self, **kwargs)
        self.rows = rows
        self.config = config
        self.url = url
        self.sortable = sortable
        self.deletable = deletable
        self.columns = OrderedDict()
        for col in columns:
            if isinstance(col, (tuple, list)):
                if len(col) == 2:
                    self.columns[col[0]] = col[1]
                    continue
            elif isinstance(col, basestring):
                self.columns[col] = prettify(col)
                continue
            raise ValueError("Column element must be either a string or 2-tuple")                

    def _set_active(self, row):
        self.model = {}
        for i, col in enumerate(self.columns.keys()):
            if i >= len(row):
                break
            self.model[col] = row[i]

    def field_label(self, name):
        return self.columns[name]

    def field_name(self, field):
        return field

    def iter_fields(self):
        for col in self.columns.keys():
            yield col

    def render(self, **kwargs):
        kwargs['grid'] = self
        return render('forms/grid_readonly.mako', kwargs)

    def render_field(self, field, readonly):
        return self.model[field]

    def row_attrs(self, i):
        return format_attrs(class_='even' if i % 2 else 'odd')

    def th_sortable(self, field):
        class_ = ''
        label = self.field_label(field)
        if self.sortable and field in self.config.get('sort_map', {}):
            class_ = 'sortable'                
            if field == self.config['sort']:
                class_ += ' sorted ' + self.config['dir']
            label = literal('<a href="#">') + label + literal('</a>')
        if class_:
            class_ = ' class="%s"' % class_
        return literal('<th' + class_ + ' field="' + field + '">') + label + literal('</th>')

    def url_attrs(self):
        return format_attrs(url=self.url)


def get_grid_config(name, request, search=None, url=None, **kwargs):
    config = {
        'actions': [],
        'per_page': 20,
        'page': 1,
        'sortable': True,
        'dir': 'asc',
        'object_url': '',
        'deletable': False,
        'delete_url': '',
        'use_dialog': False,
        }
    config.update(kwargs)
    # words = name.split('.')
    # if len(words) == 2:
    #     config.setdefault('object_url', request.route_url(words[0], action='crud'))
    #     config.setdefault('delete_url', config['object_url'])
    for key in config:
        full_key = name+'_'+key
        if request.params.get(key):
            value = request.params[key]
            config[key] = value
            request.session[full_key] = value
        elif request.session.get(full_key):
            value = request.session[full_key]
            config[key] = value
    config['request'] = request
    config['search'] = search
    config['url'] = url
    return config


def get_pager(query, config):
    query = query(config)
    count = None
    if isinstance(query, Query):
        count = query.count()
    return paginate.Page(
        query, item_count=count,
        items_per_page=int(config['per_page']),
        page=int(config['page']),
        url=paginate.PageURL(config['url'], {}),
        )


def get_sort_map(cls, names=None, **kwargs):
    """
    Convenience function which returns a sort map.
    """

    smap = {}
    if names is None:
        names = []
        for attr in cls.__dict__:
            obj = getattr(cls, attr)
            if isinstance(obj, InstrumentedAttribute):
                if obj.key != 'uuid':
                    names.append(obj.key)
    for name in names:
        smap[name] = sorter(getattr(cls, name))
    smap.update(kwargs)
    return smap


def render_grid(request, grid, search=None, **kwargs):
    if request.params.get('partial'):
        return Response(body=grid, content_type='text/html')
    kwargs['grid'] = grid
    if search:
        kwargs['search'] = SearchFormRenderer(search)
    return kwargs


def sort_query(query, config, sort_map, join_map={}):
    field = config['sort']
    joins = config.setdefault('joins', [])
    if field in join_map and field not in joins:
        query = join_map[field](query)
        joins.append(field)
    config['sort_map'] = sort_map
    return sort_map[field](query, config['dir'])


def sorter(field):
    """
    Returns a function suitable for a sort map callable, with typical
    logic built in for sorting applied to ``field``.
    """
    return lambda q, d: q.order_by(getattr(field, d)())
