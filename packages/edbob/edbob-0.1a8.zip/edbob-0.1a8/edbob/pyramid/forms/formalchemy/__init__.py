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
``edbob.pyramid.forms.formalchemy`` -- FormAlchemy Interface
"""

from __future__ import absolute_import

import datetime
import new

from pyramid.renderers import render
from webhelpers import paginate
from webhelpers.html import tags
from webhelpers.html.builder import format_attrs
from webhelpers.html.tags import literal

import formalchemy
from formalchemy import fields
from formalchemy.validators import accepts_none

import edbob
from edbob.lib import pretty
from edbob.util import prettify
from edbob.pyramid import Session, helpers

from edbob.pyramid.forms.formalchemy.fieldset import *


__all__ = ['AlchemyGrid', 'ChildGridField', 'PropertyField',
           'EnumFieldRenderer', 'PrettyDateTimeFieldRenderer',
           'AutocompleteFieldRenderer', 'FieldSet',
           'make_fieldset', 'required', 'pretty_datetime']


class TemplateEngine(formalchemy.templates.TemplateEngine):
    """
    Mako template engine for FormAlchemy.
    """

    def render(self, template, prefix='/forms/', suffix='.mako', **kwargs):
        template = ''.join((prefix, template, suffix))
        return render(template, kwargs)


# Make our TemplateEngine the default.
engine = TemplateEngine()
formalchemy.config.engine = engine


class AlchemyGrid(formalchemy.Grid):
    """
    This class defines the basic grid which you see in pretty much all
    Rattail/Pyramid apps.

    .. todo::
       This needs to be documented more fully, along with the rest of
       rattail.pyramid I suppose...
    """

    prettify = staticmethod(prettify)

    # uuid_key = None

    # def __init__(self, cls, instances, config, url_kwargs={}, *args, **kwargs):
    #     formalchemy.Grid.__init__(self, cls, instances, *args, **kwargs)
    #     self.pager = instances if isinstance(instances, paginate.Page) else None
    #     self.config = config
    #     self.url_kwargs = url_kwargs
    #     self.sortable = config.get('sortable', False)

    def __init__(self, cls, instances, config, gridurl=None, objurl=None,
                 delurl=None, **kwargs):
        """
        Grid constructor.

        ``url`` must be the URL used to access the grid itself.  This url/view
        must accept a GET query string parameter of "partial=True", which will
        indicate that the grid *only* is being requested, as opposed to the
        full page in which the grid normally resides.
        """

        formalchemy.Grid.__init__(self, cls, instances, **kwargs)
        self.config = config
        self.request = config['request']
        self.gridurl = gridurl
        self.objurl = objurl
        self.delurl = delurl
        self.sortable = config.get('sortable', False)
        self.deletable = config.get('deletable', False)
        self.pager = instances if isinstance(instances, paginate.Page) else None

    def field_name(self, field):
        return field.name

    def iter_fields(self):
        for field in self.render_fields.itervalues():
            yield field

    def render_field(self, field, readonly):
        if readonly:
            return field.render_readonly()
        return field.render()

    def row_attrs(self, i):
        attrs = dict(class_='even' if i % 2 else 'odd')
        if hasattr(self.model, 'uuid'):
            attrs['uuid'] = self.model.uuid
        return format_attrs(**attrs)

    def url_attrs(self):
        attrs = {}
        url = self.request.route_url
        if self.gridurl:
            attrs['url'] = self.gridurl
        if self.objurl:
            attrs['objurl'] = url(self.objurl, uuid='{uuid}')
        if self.delurl:
            attrs['delurl'] = url(self.delurl, uuid='{uuid}')
        return format_attrs(**attrs)

    # def render(self, class_=None, **kwargs):
    #     """
    #     Renders the grid into HTML, and returns the result.

    #     ``class_`` (if provided) is used to define the class of the ``<div>``
    #     (wrapper) and ``<table>`` elements of the grid.

    #     Any remaining ``kwargs`` are passed directly to the underlying
    #     ``formalchemy.Grid.render()`` method.
    #     """

    #     kwargs['class_'] = class_
    #     # kwargs.setdefault('get_uuid', self.get_uuid)
    #     kwargs.setdefault('checkboxes', False)
    #     return formalchemy.Grid.render(self, **kwargs)

    def render(self, **kwargs):
        engine = self.engine or formalchemy.config.engine
        if self.readonly:
            return engine('grid_readonly', grid=self, **kwargs)
        kwargs.setdefault('request', self._request)
        return engine('grid', grid=self, **kwargs)

    def th_sortable(self, field):
        class_ = ''
        label = field.label()
        if self.sortable and field.key in self.config.get('sort_map', {}):
            class_ = 'sortable'                
            if field.key == self.config['sort']:
                class_ += ' sorted ' + self.config['dir']
            label = literal('<a href="#">') + label + literal('</a>')
        if class_:
            class_ = ' class="%s"' % class_
        return literal('<th' + class_ + ' field="' + field.key + '">') + label + literal('</th>')

    # def url(self):
    #     # TODO: Probably clean this up somehow...
    #     if self.pager is not None:
    #         u = self.pager._url_generator(self.pager.page, partial=True)
    #     else:
    #         u = self._url or ''
    #     qs = self.query_string()
    #     if qs:
    #         if '?' not in u:
    #             u += '?'
    #         u += qs
    #     elif '?' not in u:
    #         u += '?partial=True'
    #     return u

    # def query_string(self):
    #     # TODO: Probably clean this up somehow...
    #     qs = ''
    #     if self.url_kwargs:
    #         for k, v in self.url_kwargs.items():
    #             qs += '&%s=%s' % (urllib.quote_plus(k), urllib.quote_plus(v))
    #     return qs

    def get_actions(self):
        """
        Returns an HTML snippet containing ``<td>`` elements for each "action"
        defined in the grid.
        """

        def get_class(text):
            return text.lower().replace(' ', '-')

        res = ''
        for action in self.config['actions']:
            if isinstance(action, basestring):
                text = action
                cls = get_class(text)
            else:
                text = action[0]
                if len(action) == 2:
                    cls = action[1]
                else:
                    cls = get_class(text)
            res += literal(
                '<td class="action %s"><a href="#">%s</a></td>' %
                (cls, text))
        return res

    # def get_uuid(self):
    #     """
    #     .. highlight:: none

    #     Returns a unique identifier for a given record, in the form of an HTML
    #     attribute for direct inclusion in a ``<tr>`` element within a template.
    #     An example of what this function might return would be the string::

    #        'uuid="420"'

    #     Rattail itself will tend to use *universally-unique* IDs (true UUIDs),
    #     but this method may be overridden to support legacy databases with
    #     auto-increment IDs, etc.  Really the only important thing is that the
    #     value returned be unique across the relevant data set.

    #     If the concept is unsupported, the method should return an empty
    #     string.
    #     """

    #     def uuid():
    #         if self.uuid_key and hasattr(self.model, self.uuid_key):
    #             return getattr(self.model, self.uuid_key)
    #         if hasattr(self.model, 'uuid'):
    #             return getattr(self.model, 'uuid')
    #         if hasattr(self.model, 'id'):
    #             return getattr(self.model, 'id')

    #     uuid = uuid()
    #     if uuid:
    #         return literal('uuid="%s"' % uuid)
    #     return ''


class ChildGridField(formalchemy.Field):
    """
    Convenience class for including a child grid within a fieldset as a
    read-only field.
    """

    def __init__(self, name, value, *args, **kwargs):
        super(ChildGridField, self).__init__(name, *args, **kwargs)
        self.set(value=value)
        self.set(readonly=True)


class PropertyField(formalchemy.Field):
    """
    Convenience class for fields which simply involve a read-only property
    value.
    """

    def __init__(self, name, attr=None, *args, **kwargs):
        super(PropertyField, self).__init__(name, *args, **kwargs)
        if not attr:
            attr = name
        self.set(value=lambda x: getattr(x, attr))
        self.set(readonly=True)


@accepts_none
def required(value, field=None):
    if value is None or value == '':
        msg = "Please provide a value"
        if field:
            msg = "You must provide a value for %s" % field.label()
        raise formalchemy.ValidationError(msg)


def EnumFieldRenderer(enum):
    """
    Adds support for enumeration fields.
    """

    class Renderer(formalchemy.fields.SelectFieldRenderer):
        
        def render_readonly(self, **kwargs):
            value = self.raw_value
            if value is None:
                return ''
            if value in enum:
                return enum[value]
            return value

        def render(self, **kwargs):
            opts = []
            for value in sorted(enum):
                opts.append((enum[value], value))
            return formalchemy.fields.SelectFieldRenderer.render(self, opts, **kwargs)

    return Renderer


def pretty_datetime(value):
    """
    Formats a ``datetime.datetime`` instance and returns a "pretty"
    human-readable string from it, e.g. "42 minutes ago".  ``value`` is
    rendered directly as a string if no date/time can be parsed from it.
    """

    if not isinstance(value, datetime.datetime):
        return str(value) if value else ''
    value = edbob.local_time(value)
    fmt = formalchemy.fields.DateTimeFieldRenderer.format
    return literal('<span title="%s">%s</span>' % (
            value.strftime(fmt),
            pretty.date(value)))    


class PrettyDateTimeFieldRenderer(formalchemy.fields.DateTimeFieldRenderer):
    """
    Adds "pretty" date/time support for FormAlchemy.
    """

    def render_readonly(self, **kwargs):
        return pretty_datetime(self.raw_value)


class DateTimeFieldRenderer(formalchemy.fields.DateTimeFieldRenderer):
    """
    Leverages edbob time system to coerce timestamp to local time zone before
    displaying it.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if isinstance(value, datetime.datetime):
            value = edbob.local_time(value)
            return value.strftime(self.format)
        print type(value)
        return ''

FieldSet.default_renderers[formalchemy.types.DateTime] = DateTimeFieldRenderer


def AutocompleteFieldRenderer(service_url, display, width='300px', callback=None, **kwargs):
    """
    Returns a field renderer class which leverages jQuery autocomplete to
    provide a more user-friendly experience.  This is typically used in place
    of a ``SelectFieldRenderer`` when the data set is deemed too large for that
    renderer.

    ``service_url`` is required and will ultimately be passed to the
    ``jQuery.autocomplete()`` function via the ``serviceUrl`` data parameter.

    ``display`` must be either a callable which accepts an object key as its
    only positional argument, or else a tuple of the form ``(Class, 'attr')``.

    ``width`` is optional but is also passed to the jQuery function.

    If ``callback`` is specified, it should be the name of a JavaScript
    function within the containing page's scope.  This is used in place of
    event handlers for autocomplete fields.
    """

    kwargs['service_url'] = service_url
    kwargs['width'] = width
    kwargs['callback'] = callback
    Renderer = new.classobj('AutocompleteFieldRenderer', (_AutocompleteFieldRenderer,), kwargs)
    if callable(display):
        Renderer.display = classmethod(display)
    else:
        Renderer.display = display
    return Renderer


class _AutocompleteFieldRenderer(fields.FieldRenderer):
    """
    Implementation for :class:`AutocompleteFieldRenderer` class.
    """

    def _display(self, value):
        if callable(self.display):
            return self.display(value)
        if not value:
            return ''
        obj = Session.query(self.display[0]).get(value)
        if not obj:
            return ''
        return getattr(obj, self.display[1])

    def render(self, **kwargs):
        autocompleter_name = 'autocompleter_%s' % self.name.replace('-', '_')
        return formalchemy.config.engine('field_autocomplete', fieldname=self.name,
                                         fieldvalue=self.value, display=self._display(self.value),
                                         autocompleter=autocompleter_name,
                                         service_url=self.service_url, width=self.width,
                                         callback=self.callback, h=helpers, **kwargs)
