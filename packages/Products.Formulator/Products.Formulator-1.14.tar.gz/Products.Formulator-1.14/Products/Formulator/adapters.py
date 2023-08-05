# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: adapters.py 48048 2011-07-18 14:03:35Z sylvain $

from five import grok
from zope.interface import Interface
from zope.component import queryMultiAdapter

from Acquisition import aq_base, Explicit
from Products.Formulator import interfaces
from Products.Formulator.Errors import FormValidationError

_marker = object()


class CustomizedField(Explicit):
    """Proxy around a native Formulator field to be able to
    programmatically change values retrieved with get_value.
    """

    def __new__(cls, field, defaults):
        if field.meta_type not in defaults:
            return field
        return Explicit.__new__(cls, field, defaults)

    def __init__(self, field, defaults):
        self._field = field
        self._defaults = defaults[field.meta_type]

    def __getattr__(self, key):
        return getattr(self._field, key)

    def get_value(self, id, **kw):
        if id in self._defaults:
            return self._defaults[id]
        return self._field.get_value(id, **kw)


class FieldValueWriter(grok.MultiAdapter):
    """Write a Formulator field data on an object.
    """
    grok.provides(interfaces.IFieldValueWriter)
    grok.implements(interfaces.IFieldValueWriter)
    grok.adapts(interfaces.IField, Interface)

    def __init__(self, field, form):
        self._field = field
        self._content = form.get_content()

    def erase(self):
        if self._field.id in self._content.__dict__:
            del self._content.__dict__[self._field.id]

    def __call__(self, value):
        self._content.__dict__[self._field.id] = value


class FieldValueReader(grok.MultiAdapter):
    """Read a Formulator field data from an object.
    """
    grok.provides(interfaces.IFieldValueReader)
    grok.implements(interfaces.IFieldValueReader)
    grok.adapts(interfaces.IField, Interface)

    def __init__(self, field, form):
        self._field = field
        self._content = form.get_content()

    def __call__(self):
        return self._content.__dict__.get(self._field.id, _marker)


class BoundField(object):
    """Bind a Formulator field to a data.
    """
    grok.implements(interfaces.IBoundField)

    def __init__(self, field, value):
        self._field = field
        self._value = value
        self.id = field.generate_field_html_id()
        self.title = field.get_value('title')
        self.description = field.get_value('description')
        self.required = False
        if 'required' in field.values:
            self.required = field.get_value('required') and True

    def serialize(self, producer):
        self._field.validator.serializeValue(
            self._field, self._value, producer)

    def deserialize(self, data, context=None):
        return self._field.validator.deserializeValue(
            self._field, data, context=context)

    def __call__(self):
        field = self._field
        # We duplicate the code of field.render to be sure to pass our
        # proxy object to the widget while rendering it.
        key = field.generate_field_key()
        value = field._get_default(key, self._value, None)
        if field.get_value('hidden'):
            return field.widget.render_hidden(field, key, value, None)
        return field.widget.render(field, key, value, None)


class BoundForm(grok.MultiAdapter):
    """Bind a Formulator field to a content. The Formulator field is
    able to edit content values.
    """
    grok.implements(interfaces.IBoundForm)
    grok.provides(interfaces.IBoundForm)
    grok.adapts(interfaces.IForm, Interface, Interface)

    def __init__(self, form, request, context):
        self.form = aq_base(form).__of__(context)
        self.request = request
        self.context = context
        self.__content = None
        self.__values = None

    def set_content(self, content):
        self.__content = content

    def get_content(self):
        if self.__content is not None:
            return self.__content
        return self.context

    def fields(self, ignore_content=True, ignore_request=True, customizations={}):
        values = {}
        if not ignore_request:
            values = self.extract()
        elif not ignore_content:
            values = self.read()
        for field in (CustomizedField(f, customizations) for f in
                      self.form.get_fields()):
            yield BoundField(field, values.get(field.id, None))

    def validate(self):
        try:
            self.__values = self.form.validate_all(self.request)
        except FormValidationError as failure:
            raise ValueError(failure.errors)
        return True

    def extract(self):
        if self.__values is None:
            self.validate()
        return self.__values

    def read(self):
        values = {}
        for field in self.form.get_fields():
            reader = queryMultiAdapter(
                (field, self), interfaces.IFieldValueReader)
            value = reader()
            if value is _marker:
                value = field.get_value('default')
            # Do we handle alternate names ?
            values[field.id] = value
        return values

    def save(self):
        values = self.extract()
        for field in self.form.get_fields():
            value = values.get(field.id, _marker)
            if value is not _marker:
                writer = queryMultiAdapter(
                    (field, self), interfaces.IFieldValueWriter)
                writer(value)

    def erase(self):
        for field in self.form.get_fields():
            writer = queryMultiAdapter(
                (field, self), interfaces.IFieldValueWriter)
            writer.erase()

