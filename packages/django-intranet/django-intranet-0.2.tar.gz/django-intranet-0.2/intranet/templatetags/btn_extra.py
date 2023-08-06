# -*- coding: utf-8 -*-
from django.conf import settings
from django import template

from intranet.components import make_btn

register = template.Library()

@register.simple_tag
def btn(**kwargs):
    return make_btn(**kwargs)
