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
``edbob.pyramid.views.crud`` -- CRUD View Function
"""

from pyramid.httpexceptions import HTTPFound

from edbob.pyramid import forms
from edbob.pyramid import Session
from edbob.util import requires_impl


class Crud(object):

    routes = ['create', 'read', 'update', 'delete']

    route_prefix = None
    url_prefix = None
    template_prefix = None
    permission_prefix = None

    def __init__(self, request):
        self.request = request

    @property
    @requires_impl(is_property=True)
    def mapped_class(self):
        pass

    @property
    @requires_impl(is_property=True)
    def home_route(self):
        pass

    @property
    def home_url(self):
        return self.request.route_url(self.home_route)

    @property
    def cancel_route(self):
        return None

    def make_fieldset(self, model, **kwargs):
        if 'action_url' not in kwargs:
            kwargs['action_url'] = self.request.current_route_url()
        if 'home_url' not in kwargs:
            kwargs['home_url'] = self.home_url
        return forms.make_fieldset(model, **kwargs)

    def fieldset(self, obj):
        return self.make_fieldset(obj)

    def post_sync(self, fs):
        pass

    def validation_failed(self, fs):
        pass

    def crud(self, model, readonly=False):

        fs = self.fieldset(model)
        if readonly:
            fs.readonly = True
        if not fs.readonly and self.request.POST:
            fs.rebind(data=self.request.params)
            if fs.validate():

                result = None

                fs.sync()
                result = self.post_sync(fs)
                if not result:
                    Session.add(fs.model)
                    Session.flush()
                    self.request.session.flash('%s "%s" has been %s.' % (
                            fs.crud_title, fs.get_display_text(),
                            'updated' if fs.edit else 'created'))

                if result:
                    return result

                if self.request.params.get('add-another') == '1':
                    return HTTPFound(location=self.request.current_route_url())

                return HTTPFound(location=self.home_url)

            self.validation_failed(fs)

        if not fs.edit:
            fs.allow_continue = True

        return {'fieldset': fs, 'crud': True}

    def create(self):
        return self.crud(self.mapped_class)

    def read(self):
        uuid = self.request.matchdict['uuid']
        model = Session.query(self.mapped_class).get(uuid) if uuid else None
        assert model
        return self.crud(model, readonly=True)

    def update(self):
        uuid = self.request.matchdict['uuid']
        model = Session.query(self.mapped_class).get(uuid) if uuid else None
        assert model
        return self.crud(model)

    def delete(self):
        uuid = self.request.matchdict['uuid']
        model = Session.query(self.mapped_class).get(uuid) if uuid else None
        assert model
        Session.delete(model)
        return HTTPFound(location=self.home_url)

    @classmethod
    def add_routes(cls, config):
        route_name_prefix = cls.route_prefix or cls.mapped_class.__name__.lower()
        route_url_prefix = cls.url_prefix or '/%ss' % route_name_prefix
        renderer_prefix = cls.template_prefix or route_url_prefix
        permission_prefix = cls.permission_prefix or '%ss' % route_name_prefix

        for route in cls.routes:
            kw = dict(
                attr=route,
                route_name='%s.%s' % (route_name_prefix, route),
                renderer='%s/%s.mako' % (renderer_prefix, route),
                permission='%s.%s' % (permission_prefix, route),
                )
            if route == 'create':
                config.add_route(kw['route_name'], '%s/new' % route_url_prefix)
            else:
                config.add_route(kw['route_name'], '%s/{uuid}/%s' % (route_url_prefix, route))
            config.add_view(cls, http_cache=0, **kw)
