# -*- coding: utf-8 -*-
from django.db import models

from forms import MinutesField as MinutesFormField


class MinutesField(models.PositiveIntegerField):
    """
    This is simply an extension of a ``PositiveIntegerField`` that will use a 
    ``forms.MinutesField`` in forms.
    """

    description = "A field representing a duration in minutes"

    def formfield(self, **kwargs):
        defaults = {'form_class': MinutesFormField}
        defaults.update(kwargs)
        return super(MinutesField, self).formfield(**defaults)


class EnumIntegerField(models.PositiveIntegerField):
    """
    Extension of a standard Django ``PositiveIntegerField`` that takes an
    optional ``enum`` argument which should point to an implementation of
    ``stdfields.models.Enumeration``.

    The results of the implementation's ``all`` method will be used as the
    possible choices.
    """

    description = "An enumeration of integer values"

    def __init__(self, *args, **kwargs):
        if 'enum' in kwargs:
            self.enum = kwargs.pop('enum')
            kwargs['choices'] = self.enum.all()
        super(EnumIntegerField, self).__init__(*args, **kwargs)


class EnumCharField(models.CharField):
    """
    Extension of a standard Django ``CharField`` that takes an optional
    ``enum`` argument which should point to an implementation of
    ``stdfields.models.Enumeration``.

    The results of the implementation's ``all`` method will be used as the
    possible choices.
    """

    description = "An enumeration of character values"

    def __init__(self, *args, **kwargs):
        if 'enum' in kwargs:
            self.enum = kwargs.pop('enum')
            choices = self.enum.all()
            kwargs['choices'] = choices
        else:
            choices = kwargs.get('choices', [])
        super(EnumCharField, self).__init__(*args, **kwargs)


try:
    # Let South know it should be able to handle these fields
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^stdfields\.fields\.MinutesField"])
    add_introspection_rules([], ["^stdfields\.fields\.EnumIntegerField"])
    add_introspection_rules([], ["^stdfields\.fields\.EnumCharField"])
except ImportError:
    # You're not using South?!
    pass
