# -*- coding: utf-8 -*-
from django.forms.widgets import TextInput


def format_minutes(value):
    """Formats an integer as hours and minutes: ``hh:mm``."""
    if value is None or value == '':
        return u''
    try:
        value = int(value)
    except ValueError:
        return value
    divided = MinutesWidget.divide(value)
    return u'%d:%02d' % divided


class MinutesWidget(TextInput):
    """Widgets for minute fields."""

    def _format_value(self, value):
        return format_minutes(value)

    @classmethod
    def divide(cls, total):
        if total <= 0:
            return (0, 0)
        hours = 0 if total <= 60 else total / 60
        return (hours, total - (hours * 60))
