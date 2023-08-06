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
``edbob.pyramid.views.users`` -- User Views
"""

import transaction
from pyramid.httpexceptions import HTTPFound

import formalchemy
from formalchemy.fields import SelectFieldRenderer
from webhelpers.html import literal
from webhelpers.html.tags import hidden, link_to, password

import edbob
from edbob.db.auth import set_user_password
from edbob.pyramid import filters
from edbob.pyramid import forms
from edbob.pyramid import grids
from edbob.pyramid import Session


def filter_map():
    return filters.get_filter_map(
        edbob.User,
        ilike=['username'],
        person=filters.filter_ilike(edbob.Person.display_name))

def search_config(request, fmap):
    return filters.get_search_config(
        'users.list', request, fmap,
        include_filter_username=True,
        filter_type_username='lk')

def search_form(config):
    return filters.get_search_form(config)

def grid_config(request, search, fmap):
    return grids.get_grid_config(
        'users.list', request, search,
        filter_map=fmap, sort='username')

def sort_map():
    return grids.get_sort_map(
        edbob.User, ['username'],
        person=grids.sorter(edbob.Person.display_name))

def query(config):
    jmap = {'person': lambda q: q.outerjoin(edbob.Person)}
    smap = sort_map()
    q = Session.query(edbob.User)
    q = filters.filter_query(q, config, jmap)
    q = grids.sort_query(q, config, smap, jmap)
    return q


def users(context, request):

    fmap = filter_map()
    config = search_config(request, fmap)
    search = search_form(config)
    config = grid_config(request, search, fmap)
    users = grids.get_pager(query, config)

    g = forms.AlchemyGrid(
        edbob.User, users, config,
        gridurl=request.route_url('users.list'),
        objurl='user.edit')

    g.configure(
        include=[
            g.username,
            g.person,
            ],
        readonly=True)

    grid = g.render(class_='clickable users')
    return grids.render_grid(request, grid, search)


class _RolesFieldRenderer(SelectFieldRenderer):

    def render_readonly(self, **kwargs):
        roles = Session.query(edbob.Role)
        res = literal('<ul>')
        for uuid in self.value:
            role = roles.get(uuid)
            res += literal('<li>%s</li>' % (
                    link_to(role.name,
                            self.request.route_url('role.edit', uuid=role.uuid))))
        res += literal('</ul>')
        return res


def RolesFieldRenderer(request):
    return type('RolesFieldRenderer', (_RolesFieldRenderer,), {'request': request})


class RolesField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('options', self.get_options())
        kwargs.setdefault('multiple', True)
        super(RolesField, self).__init__(name, **kwargs)

    def get_value(self, user):
        return [x.uuid for x in user.roles]

    def get_options(self):
        q = Session.query(edbob.Role.name, edbob.Role.uuid)
        q = q.order_by(edbob.Role.name)
        return q.all()

    def sync(self):
        if not self.is_readonly():
            user = self.model
            roles = Session.query(edbob.Role)
            data = self.renderer.deserialize()
            user.roles = [roles.get(x) for x in data]
                

class _ProtectedPersonRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        res = str(self.person)
        res += hidden('User--person_uuid',
                      value=self.field.parent.person_uuid.value)
        return res


def ProtectedPersonRenderer(uuid):
    person = Session.query(edbob.Person).get(uuid)
    assert person
    return type('ProtectedPersonRenderer', (_ProtectedPersonRenderer,),
                {'person': person})


class _LinkedPersonRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        return link_to(str(self.raw_value),
                       self.request.route_url('person.edit', uuid=self.value))


def LinkedPersonRenderer(request):
    return type('LinkedPersonRenderer', (_LinkedPersonRenderer,), {'request': request})


class PasswordFieldRenderer(formalchemy.PasswordFieldRenderer):

    def render(self, **kwargs):
        return password(self.name, value='', maxlength=self.length, **kwargs)


def passwords_match(value, field):
    if field.parent.confirm_password.value != value:
        raise formalchemy.ValidationError("Passwords do not match")
    return value


class PasswordField(formalchemy.Field):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('value', lambda x: x.password)
        kwargs.setdefault('renderer', PasswordFieldRenderer)
        kwargs.setdefault('validate', passwords_match)
        super(PasswordField, self).__init__(*args, **kwargs)

    def sync(self):
        if not self.is_readonly():
            password = self.renderer.deserialize()
            if password:
                set_user_password(self.model, password)


def user_fieldset(user, request):
    fs = forms.make_fieldset(user, url=request.route_url,
                             url_action=request.current_route_url(),
                             route_name='users.list')

    fs.append(PasswordField('password'))
    fs.append(formalchemy.Field('confirm_password',
                                renderer=PasswordFieldRenderer))

    fs.append(RolesField(
            'roles', renderer=RolesFieldRenderer(request)))

    fs.configure(
        include=[
            fs.person,
            fs.username,
            fs.password.label("Set Password"),
            fs.confirm_password,
            fs.roles,
            ])

    if isinstance(user, edbob.User) and user.person:
        fs.person.set(readonly=True,
                      renderer=LinkedPersonRenderer(request))

    return fs


def new_user(request):
    """
    View for creating a new :class:`edbob.User` instance.
    """

    fs = user_fieldset(edbob.User, request)
    if request.POST:
        fs.rebind(data=request.params)
        if fs.validate():

            with transaction.manager:
                Session.add(fs.model)
                fs.sync()
                request.session.flash("%s \"%s\" has been %s." % (
                        fs.crud_title, fs.get_display_text(),
                        'updated' if fs.edit else 'created'))
                home = request.route_url('users.list')

            return HTTPFound(location=home)

        if fs.person_uuid.value:
            fs.person.set(readonly=True,
                          renderer=ProtectedPersonRenderer(fs.person_uuid.value))

    return {'fieldset': fs, 'crud': True}


def edit_user(request):
    uuid = request.matchdict['uuid']
    user = Session.query(edbob.User).get(uuid) if uuid else None
    assert user

    fs = user_fieldset(user, request)
    if request.POST:
        fs.rebind(data=request.params)
        if fs.validate():

            with transaction.manager:
                Session.add(fs.model)
                fs.sync()
                request.session.flash("%s \"%s\" has been %s." % (
                        fs.crud_title, fs.get_display_text(),
                        'updated' if fs.edit else 'created'))
                home = request.route_url('users.list')

            return HTTPFound(location=home)

    return {'fieldset': fs, 'crud': True}


def includeme(config):

    config.add_route('users.list', '/users')
    config.add_view(users, route_name='users.list', renderer='/users/index.mako',
                    permission='users.list', http_cache=0)

    config.add_route('user.new', '/users/new')
    config.add_view(new_user, route_name='user.new', renderer='/users/user.mako',
                    permission='users.create', http_cache=0)

    config.add_route('user.edit', '/users/{uuid}/edit')
    config.add_view(edit_user, route_name='user.edit', renderer='/users/user.mako',
                    permission='users.edit', http_cache=0)
