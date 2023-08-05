# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template

from stdfields.widgets import format_minutes

register = template.Library()


@register.filter
def minutes(value):
    return format_minutes(value)
