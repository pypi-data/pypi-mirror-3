# -*- coding: utf-8 -*-
from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def intranet_title():
    return getattr(settings, 'INTRANET_TITLE', '')

@register.simple_tag
def title():
    return ' - '.join((getattr(settings, 'INTRANET_TITLE', ''),
                       getattr(settings, 'SITE_NAME', '')))

@register.assignment_tag(takes_context=True)
def has_perm(context, perm=None, prefix=False, user=None, obj=None):
    # If not user in param, get user in context
    if not user:
        user = context.get('user', None)
    # If not user => Not authorized
    if not user :
        return False

    # First case, `perm` in param
    if perm:
        app, perm_name = perm.split('.', 1)
        # Add prefix if in param
        if prefix:
            perm_name = u'%s_%s' % (prefix, perm_name)
        # If not app_label, add the context app_label
        if not app:
            app_label = context.get('app_label', None)
            if app_label:
                complete_perm = u'%s.%s' % (app_label, perm_name)
            else:
                complete_perm = perm_name
        else:
            complete_perm = perm_name
        # Check first global permissions
        is_authorized =  user.has_perm(complete_perm)
        # Check object permissions
        if not is_authorized and obj:
            is_authorized =  user.has_perm(perm_name, obj=obj)
        return is_authorized
    # Case #2 : not `perm` param but just `prefix`
    if prefix:
        module_name = context.get('module_name', None)
        if module_name:
            perm_name = u'%s_%s' % (prefix, module_name)
        else:
            perm_name = prefix
        app_label = context.get('app_label', None)
        if app_label:
            complete_perm = u'%s.%s' % (app_label, perm_name)
        else:
            complete_perm = perm_name
        is_authorized = user.has_perm(complete_perm)
        if not is_authorized and obj:
            is_authorized = user.has_perm(perm_name, obj)
        return is_authorized

    return False


@register.simple_tag
def default_table_class():
    return u'table table-striped table-bordered'
