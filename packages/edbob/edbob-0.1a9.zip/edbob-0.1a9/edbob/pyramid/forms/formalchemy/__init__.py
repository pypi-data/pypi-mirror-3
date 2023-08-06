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
from webhelpers.html.tags import literal

import formalchemy
from formalchemy.validators import accepts_none

from edbob.lib import pretty
from edbob.pyramid import Session, helpers
from edbob.time import localize

from edbob.pyramid.forms.formalchemy.fieldset import *
from edbob.pyramid.forms.formalchemy.fields import *
from edbob.pyramid.forms.formalchemy.renderers import *


__all__ = ['ChildGridField', 'PropertyField', 'EnumFieldRenderer',
           'PrettyDateTimeFieldRenderer', 'AutocompleteFieldRenderer',
           'FieldSet', 'make_fieldset', 'required', 'pretty_datetime',
           'AssociationProxyField']


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


def pretty_datetime(value, from_='local', to='local'):
    """
    Formats a ``datetime.datetime`` instance and returns a "pretty"
    human-readable string from it, e.g. "42 minutes ago".  ``value`` is
    rendered directly as a string if no date/time can be parsed from it.
    """

    if not isinstance(value, datetime.datetime):
        return str(value) if value else ''
    if not value.tzinfo:
        value = localize(value, from_=from_, to=to)
    return literal('<span title="%s">%s</span>' % (
            value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
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


class _AutocompleteFieldRenderer(formalchemy.fields.FieldRenderer):
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
