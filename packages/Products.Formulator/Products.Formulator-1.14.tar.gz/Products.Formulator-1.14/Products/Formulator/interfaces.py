# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py 47946 2011-06-17 13:19:15Z sylvain $

from zope import interface


class IField(interface.Interface):
    """A formulator field.
    """
    id = interface.Attribute(u"Field identifier")

    def serialize(producer):
        """ serialize field value and push it to the producer
        """

    def deserialize(value):
        """ deserialize the value
        """


class IForm(interface.Interface):
    """A formulator form.
    """


class IFieldValueWriter(interface.Interface):
    """Write a field value on a content.
    """

    def __init__(field, content):
        """Adapt the given field and content.
        """

    def __call__(value):
        """Save formulator value on the given content.
        """


class IFieldValueReader(interface.Interface):
    """Read a field value from a content.
    """

    def __init__(field, content):
        """Adapt the given field and content.
        """

    def __call__():
        """Read the given value.
        """


class IBoundField(interface.Interface):
    """Return field information.
    """
    id = interface.Attribute("HTML ID")
    title = interface.Attribute("Field title")
    description = interface.Attribute("Field description")
    required = interface.Attribute("Is the field required ?")

    def __call__():
        """Render field HTML value.
        """


class IBoundForm(interface.Interface):
    """Manage access to a formulator.
    """

    def __init__(form, request, content):
        """Adapt a formulator form, a request and a content.
        """

    def fields(ignore_content=False, ignore_request=False):
        """Return the fields as IBoundFields.
        """

    def validate():
        """Validate the form fields using request data.
        """

    def extract():
        """Validate and extract the form fields using request
        data. Return data or raise an exception in case of validation
        error.
        """

    # Those two last manage reading / writing values on an object.

    def get_content():
        """Return content used to read and save values. It is the
        context unless some other object have been set using
        ``set_content``.
        """

    def set_content(content):
        """Set content as content used to read and save values.
        """

    def read():
        """Return data saved on the content.
        """

    def save():
        """Validate, extract and save data on the content, or raise an
        exception in case of validation error.
        """

    def erase():
        """Erase all stored values from the content.
        """
