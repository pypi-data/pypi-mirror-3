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

from pyramid.renderers import render
from webhelpers import paginate
from webhelpers.html.builder import format_attrs
from webhelpers.html.tags import literal

import formalchemy
from formalchemy.validators import accepts_none

import edbob
from edbob.lib import pretty
from edbob.util import prettify
from edbob.pyramid import Session


__all__ = ['AlchemyGrid', 'ChildGridField', 'PropertyField',
           'EnumFieldRenderer', 'PrettyDateTimeFieldRenderer',
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


class FieldSet(formalchemy.FieldSet):
    """
    Adds a little magic to the ``FieldSet`` class.
    """

    prettify = staticmethod(prettify)

    def __init__(self, model, class_name=None, crud_title=None, url=None,
                 route_name=None, url_action=None, url_cancel=None, **kwargs):
        formalchemy.FieldSet.__init__(self, model, **kwargs)
        self.class_name = class_name or self._original_cls.__name__.lower()
        self.crud_title = crud_title or prettify(self.class_name)
        self.edit = isinstance(model, self._original_cls)
        self.route_name = route_name or (self.class_name + 's')
        self.url_action = url_action or url(self.route_name)
        self.url_cancel = url_cancel or url(self.route_name)

    def get_display_text(self):
        return unicode(self.model)

    def render(self, **kwargs):
        kwargs.setdefault('class_', self.class_name)
        return formalchemy.FieldSet.render(self, **kwargs)


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


def make_fieldset(model, **kwargs):
    kwargs.setdefault('session', Session())
    return FieldSet(model, **kwargs)


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
