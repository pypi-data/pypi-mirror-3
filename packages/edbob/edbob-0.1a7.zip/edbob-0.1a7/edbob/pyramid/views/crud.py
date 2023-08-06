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

# from pyramid.renderers import render_to_response
# from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPOk, HTTPUnauthorized
# import transaction
from pyramid.httpexceptions import HTTPFound

# import sqlahelper

# # import rattail.pyramid.forms.util as util
# from rattail.db.perms import has_permission
# from rattail.pyramid.forms.formalchemy import Grid

import edbob
from edbob.db import Base
from edbob.pyramid import forms
from edbob.pyramid import Session
from edbob.util import requires_impl


class Crud(object):

    routes = ['new', 'edit', 'delete']

    route_prefix = None
    url_prefix = None
    template_prefix = None

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

    @property
    def permission_prefix(self):
        return self.route_prefix + 's'

    def make_fieldset(self, model, **kwargs):
        if 'action_url' not in kwargs:
            kwargs['action_url'] = self.request.current_route_url()
        if 'home_url' not in kwargs:
            kwargs['home_url'] = self.home_url
        return forms.make_fieldset(model, **kwargs)

    def fieldset(self, obj):
        """
        Creates, configures and returns the fieldset.

        .. note::
           You more than likely will want to override this.
        """

        return self.make_fieldset(obj)

    def post_sync(self, fs):
        pass

    def validation_failed(self, fs):
        pass

    def crud(self, obj=None):
        if obj is None:
            obj = self.mapped_class

        # fs = self.fieldset(obj)
        # if not fs.readonly and self.request.POST:
        #     fs.rebind(data=self.request.params)
        #     if fs.validate():

        #         with transaction.manager:
        #             fs.sync()
        #             Session.add(fs.model)
        #             Session.flush()
        #             self.request.session.flash('%s "%s" has been %s.' % (
        #                     fs.crud_title, fs.get_display_text(),
        #                     'updated' if fs.edit else 'created'))

        #         if self.request.params.get('add-another') == '1':
        #             return HTTPFound(location=self.request.current_route_url())

        #         return HTTPFound(location=self.home_url)

        fs = self.fieldset(obj)
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

        # TODO: This probably needs attention.
        if not fs.edit:
            fs.allow_continue = True

        return {'fieldset': fs, 'crud': True}

    def new(self):
        return self.crud(self.mapped_class)

    def edit(self):
        uuid = self.request.matchdict['uuid']
        obj = Session.query(self.mapped_class).get(uuid) if uuid else None
        assert obj
        return self.crud(obj)

    def delete(self):
        uuid = self.request.matchdict['uuid']
        obj = Session.query(self.mapped_class).get(uuid) if uuid else None
        assert obj
        Session.delete(obj)
        return HTTPFound(location=self.home_url)

    @classmethod
    def add_routes(cls, config):
        """
        Add routes to the config object.
        """

        routes = cls.routes
        if isinstance(routes, list):
            _routes = routes
            routes = {}
            for route in _routes:
                routes[route] = {}

        route_prefix = cls.route_prefix or cls.mapped_class.__name__.lower()
        url_prefix = cls.url_prefix or '/%ss' % route_prefix
        template_prefix = cls.template_prefix or url_prefix
        permission_prefix = cls.permission_prefix or '%ss' % route_prefix

        for action in routes:
            kw = dict(
                route='%s.%s' % (route_prefix, action),
                renderer='%s/%s.mako' % (template_prefix, action),
                permission='%s.%s' % (permission_prefix, dict(new='create').get(action, action)),
                )
            if action == 'new':
                kw['url'] = '%s/new' % url_prefix
            else:
                kw['url'] = '%s/{uuid}/%s' % (url_prefix, action)
            kw.update(routes[action])
            config.add_route(kw['route'], kw['url'])
            config.add_view(cls, attr=action, route_name=kw['route'], renderer=kw['renderer'],
                            permission=kw['permission'], http_cache=0)
        

# def crud(request, cls, fieldset_factory, home=None, delete=None, post_sync=None, pre_render=None):
#     """
#     Adds a common CRUD mechanism for objects.

#     ``cls`` should be a SQLAlchemy-mapped class, presumably deriving from
#     :class:`edbob.Object`.

#     ``fieldset_factory`` must be a callable which accepts the fieldset's
#     "model" as its only positional argument.

#     ``home`` will be used as the redirect location once a form is fully
#     validated and data saved.  If you do not speficy this parameter, the
#     user will be redirected to be the CRUD page for the new object (e.g. so
#     an object may be created before certain properties may be edited).

#     ``delete`` may either be a string containing a URL to which the user
#     should be redirected after the object has been deleted, or else a
#     callback which will be executed *instead of* the normal algorithm
#     (which is merely to delete the object via the Session).

#     ``post_sync`` may be a callback which will be executed immediately
#     after :meth:`FieldSet.sync()` is called, i.e. after validation as well.

#     ``pre_render`` may be a callback which will be executed after any POST
#     processing has occured, but just before rendering.
#     """

#     uuid = request.params.get('uuid')
#     obj = Session.query(cls).get(uuid) if uuid else cls
#     assert obj

#     if request.params.get('delete'):
#         if delete:
#             if isinstance(delete, basestring):
#                 with transaction.manager:
#                     Session.delete(obj)
#                 return HTTPFound(location=delete)
#             with transaction.manager:
#                 res = delete(obj)
#             if res:
#                 return res
#         else:
#             with transaction.manager:
#                 Session.delete(obj)
#             if not home:
#                 raise ValueError("Must specify 'home' or 'delete' url "
#                                  "in call to crud()")
#             return HTTPFound(location=home)

#     fs = fieldset_factory(obj)

#     # if not fs.readonly and self.request.params.get('fieldset'):
#     #     fs.rebind(data=self.request.params)
#     #     if fs.validate():
#     #         fs.sync()
#     #         if post_sync:
#     #             res = post_sync(fs)
#     #             if isinstance(res, HTTPFound):
#     #                 return res
#     #         if self.request.params.get('partial'):
#     #             self.Session.flush()
#     #             return self.json_success(uuid=fs.model.uuid)
#     #         return HTTPFound(location=self.request.route_url(objects, action='index'))

#     if not fs.readonly and request.POST:
#         fs.rebind(data=request.params)
#         if fs.validate():
#             with transaction.manager:
#                 fs.sync()
#                 if post_sync:
#                     res = post_sync(fs)
#                     if res:
#                         return res

#                 if request.params.get('partial'):
#                     # Session.flush()
#                     # return self.json_success(uuid=fs.model.uuid)
#                     assert False, "need to fix this"

#                 if not home:
#                     fs.model = Session.merge(fs.model)
#                     home = request.current_route_url(uuid=fs.model.uuid)
#                     request.session.flash("%s \"%s\" has been %s." % (
#                             fs.crud_title, fs.get_display_text(),
#                             'updated' if fs.edit else 'created'))
#             return HTTPFound(location=home)

#     data = {'fieldset': fs, 'crud': True}

#     if pre_render:
#         res = pre_render(fs)
#         if res:
#             if isinstance(res, HTTPException):
#                 return res
#             data.update(res)

#     # data = {'fieldset':fs}
#     # if self.request.params.get('partial'):
#     #     return render_to_response('/%s/crud_partial.mako' % objects,
#     #                               data, request=self.request)
#     # return data

#     return data


# class needs_perm(object):
#     """
#     Decorator to be used for handler methods which should restrict access based
#     on the current user's permissions.
#     """

#     def __init__(self, permission, **kwargs):
#         self.permission = permission
#         self.kwargs = kwargs

#     def __call__(self, fn):
#         permission = self.permission
#         kw = self.kwargs
#         def wrapped(self):
#             if not self.request.current_user:
#                 self.request.session['referrer'] = self.request.url_generator.current()
#                 self.request.session.flash("You must be logged in to do that.", 'error')
#                 return HTTPFound(location=self.request.route_url('login'))
#             if not has_permission(self.request.current_user, permission):
#                 self.request.session.flash("You do not have permission to do that.", 'error')
#                 home = kw.get('redirect', self.request.route_url('home'))
#                 return HTTPFound(location=home)
#             return fn(self)
#         return wrapped


# def needs_user(fn):
#     """
#     Decorator for handler methods which require simply that a user be currently
#     logged in.
#     """

#     def wrapped(self):
#         if not self.request.current_user:
#             self.request.session['referrer'] = self.request.url_generator.current()
#             self.request.session.flash("You must be logged in to do that.", 'error')
#             return HTTPFound(location=self.request.route_url('login'))
#         return fn(self)
#     return wrapped


# class Handler(object):

#     def __init__(self, request):
#         self.request = request
#         self.Session = sqlahelper.get_session()

#     # def json_response(self, data={}):
#     #     response = render_to_response('json', data, request=self.request)
#     #     response.headers['Content-Type'] = 'application/json'
#     #     return response


# class CrudHandler(Handler):
#     # """
#     # This handler provides all the goodies typically associated with general
#     # CRUD functionality, e.g. search filters and grids.
#     # """

#     def crud(self, cls, fieldset_factory, home=None, delete=None, post_sync=None, pre_render=None):
#         """
#         Adds a common CRUD mechanism for objects.

#         ``cls`` should be a SQLAlchemy-mapped class, presumably deriving from
#         :class:`rattail.Object`.

#         ``fieldset_factory`` must be a callable which accepts the fieldset's
#         "model" as its only positional argument.

#         ``home`` will be used as the redirect location once a form is fully
#         validated and data saved.  If you do not speficy this parameter, the
#         user will be redirected to be the CRUD page for the new object (e.g. so
#         an object may be created before certain properties may be edited).

#         ``delete`` may either be a string containing a URL to which the user
#         should be redirected after the object has been deleted, or else a
#         callback which will be executed *instead of* the normal algorithm
#         (which is merely to delete the object via the Session).

#         ``post_sync`` may be a callback which will be executed immediately
#         after ``FieldSet.sync()`` is called, i.e. after validation as well.

#         ``pre_render`` may be a callback which will be executed after any POST
#         processing has occured, but just before rendering.
#         """

#         uuid = self.request.params.get('uuid')
#         obj = self.Session.query(cls).get(uuid) if uuid else cls
#         assert obj

#         if self.request.params.get('delete'):
#             if delete:
#                 if isinstance(delete, basestring):
#                     self.Session.delete(obj)
#                     return HTTPFound(location=delete)
#                 res = delete(obj)
#                 if res:
#                     return res
#             else:
#                 self.Session.delete(obj)
#                 if not home:
#                     raise ValueError("Must specify 'home' or 'delete' url "
#                                      "in call to CrudHandler.crud()")
#                 return HTTPFound(location=home)

#         fs = fieldset_factory(obj)

#         # if not fs.readonly and self.request.params.get('fieldset'):
#         #     fs.rebind(data=self.request.params)
#         #     if fs.validate():
#         #         fs.sync()
#         #         if post_sync:
#         #             res = post_sync(fs)
#         #             if isinstance(res, HTTPFound):
#         #                 return res
#         #         if self.request.params.get('partial'):
#         #             self.Session.flush()
#         #             return self.json_success(uuid=fs.model.uuid)
#         #         return HTTPFound(location=self.request.route_url(objects, action='index'))

#         if not fs.readonly and self.request.POST:
#             # print self.request.POST
#             fs.rebind(data=self.request.params)
#             if fs.validate():
#                 fs.sync()
#                 if post_sync:
#                     res = post_sync(fs)
#                     if res:
#                         return res
#                 if self.request.params.get('partial'):
#                     self.Session.flush()
#                     return self.json_success(uuid=fs.model.uuid)

#                 if not home:
#                     self.Session.flush()
#                     home = self.request.url_generator.current() + '?uuid=' + fs.model.uuid
#                     self.request.session.flash("%s \"%s\" has been %s." % (
#                             fs.crud_title, fs.get_display_text(),
#                             'updated' if fs.edit else 'created'))
#                 return HTTPFound(location=home)

#         data = {'fieldset': fs, 'crud': True}

#         if pre_render:
#             res = pre_render(fs)
#             if res:
#                 if isinstance(res, HTTPException):
#                     return res
#                 data.update(res)

#         # data = {'fieldset':fs}
#         # if self.request.params.get('partial'):
#         #     return render_to_response('/%s/crud_partial.mako' % objects,
#         #                               data, request=self.request)
#         # return data

#         return data

#     def grid(self, *args, **kwargs):
#         """
#         Convenience function which returns a grid.  The only functionality this
#         method adds is the ``session`` parameter.
#         """

#         return Grid(session=self.Session(), *args, **kwargs)

#     # def get_grid(self, name, grid, query, search=None, url=None, **defaults):
#     #     """
#     #     Convenience function for obtaining the configuration for a grid,
#     #     and then obtaining the grid itself.

#     #     ``name`` is essentially the config key, e.g. ``'products.lookup'``, and
#     #     in fact is expected to take that precise form (where the first part is
#     #     considered the handler name and the second part the action name).

#     #     ``grid`` must be a callable with a signature of ``grid(query,
#     #     config)``, and ``query`` will be passed directly to the ``grid``
#     #     callable.  ``search`` will be used to inform the grid of the search in
#     #     effect, if any. ``defaults`` will be used to customize the grid config.
#     #     """

#     #     if not url:
#     #         handler, action = name.split('.')
#     #         url = self.request.route_url(handler, action=action)
#     #     config = util.get_grid_config(name, self.request, search,
#     #                                   url=url, **defaults)
#     #     return grid(query, config)

#     # def get_search_form(self, name, labels={}, **defaults):
#     #     """
#     #     Convenience function for obtaining the configuration for a search form,
#     #     and then obtaining the form itself.

#     #     ``name`` is essentially the config key, e.g. ``'products.lookup'``.
#     #     The ``labels`` dictionary can be used to override the default labels
#     #     displayed for the various search fields.  The ``defaults`` dictionary
#     #     is used to customize the search config.
#     #     """

#     #     config = util.get_search_config(name, self.request,
#     #                                     self.filter_map(), **defaults)
#     #     form = util.get_search_form(config, **labels)
#     #     return form

#     # def object_crud(self, cls, objects=None, post_sync=None):
#     #     """
#     #     This method is a desperate attempt to encapsulate shared CRUD logic
#     #     which is useful across all editable data objects.

#     #     ``objects``, if provided, should be the plural name for the class as
#     #     used in internal naming, e.g. ``'products'``.  A default will be used
#     #     if you do not provide this value.

#     #     ``post_sync``, if provided, should be a callable which accepts a
#     #     ``formalchemy.Fieldset`` instance as its only argument.  It will be
#     #     called immediately after the fieldset is synced.
#     #     """

#     #     if not objects:
#     #         objects = cls.__name__.lower() + 's'

#     #     uuid = self.request.params.get('uuid')
#     #     obj = self.Session.query(cls).get(uuid) if uuid else cls
#     #     assert obj

#     #     fs = self.fieldset(obj)

#     #     if not fs.readonly and self.request.params.get('fieldset'):
#     #         fs.rebind(data=self.request.params)
#     #         if fs.validate():
#     #             fs.sync()
#     #             if post_sync:
#     #                 res = post_sync(fs)
#     #                 if isinstance(res, HTTPFound):
#     #                     return res
#     #             if self.request.params.get('partial'):
#     #                 self.Session.flush()
#     #                 return self.json_success(uuid=fs.model.uuid)
#     #             return HTTPFound(location=self.request.route_url(objects, action='index'))

#     #     data = {'fieldset':fs}
#     #     if self.request.params.get('partial'):
#     #         return render_to_response('/%s/crud_partial.mako' % objects,
#     #                                   data, request=self.request)
#     #     return data

#     # def render_grid(self, grid, search=None, **kwargs):
#     #     """
#     #     Convenience function to render a standard grid.  Really just calls
#     #     :func:`dtail.forms.util.render_grid()`.
#     #     """

#     #     return util.render_grid(self.request, grid, search, **kwargs)
