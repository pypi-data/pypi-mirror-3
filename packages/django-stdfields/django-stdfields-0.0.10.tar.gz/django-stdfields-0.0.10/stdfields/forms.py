# -*- coding: utf-8 -*-
from __future__ import division
import re

from django import forms
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from widgets import MinutesWidget


class MinutesField(forms.IntegerField):
    """
    A form field representing a duration in minutes.

    Accepts formats ``hh:mm`` and ``hh.fraction``, meaning ``8:30`` and ``8.5``
    are equivalent, meaning 8 hours and 30 minutes.
    """
    widget = MinutesWidget

    def __init__(self, *args, **kwargs):
        # Override the default 'invalid' error message from IntegerField
        if 'error_messages' in kwargs:
            error_messages = kwargs.pop('error_messages')
        else:
            error_messages = {}
        if not 'invalid' in error_messages:
            error_messages['invalid'] = _(u'Enter a valid value.')
        kwargs['error_messages'] = error_messages
        super(MinutesField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = smart_str(value).strip()
        match = re.search(r'^(\d+):(\d{1,2})$', value)
        if match:
            groups = match.groups()
            hours = int(groups[0])
            minutes = int(groups[1])
            if minutes > 59:
                msg = self.error_messages['invalid']
                raise forms.ValidationError(msg)
            value = (hours * 60) + minutes
        else:
            value = value.replace(',', '.')
            if not '.' in value:
                value = u'%s.0' % (value)
            parts = value.split('.')
            try:
                hours = int(parts[0])
                fraction = int(parts[1])
                if not fraction in (0, 5, 25, 50, 75):
                    msg = self.error_messages['invalid']
                    raise forms.ValidationError(msg)
                if fraction == 5:
                    fraction = 50
                value = int((hours * 60) + (60 / 100 * fraction))
            except (ValueError, TypeError):
                msg = self.error_messages['invalid']
                raise forms.ValidationError(msg)
        return super(MinutesField, self).clean(value)
