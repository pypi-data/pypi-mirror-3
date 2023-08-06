# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def list_header(context, list_display=None):
    if not list_display:
        list_display = context.get('list_display', [])
    header = ''
    if list_display:
        for field in list_display:
            ordering = field.get('ordering', False)
            if ordering:
                if field.get('ordering_asc', False):
                    ordering_icon = 'icon-chevron-down'
                else:
                    ordering_icon = 'icon-chevron-up'
                ordering_html = '<span class="pull-right"><i class="%s"></i></span>' % (
                    ordering_icon)
            else:
                ordering_html = ''

            if field.get('callable', False) and 'short_description' in field:
                field_verbose_name = field.getattr('short_description')
            else:
                field_verbose_name = field['verbose_name'].capitalize()
                
            header += u'<th><a href="%s">%s%s</a></th>' % (field.get('ordering_url', ''),
                                                           field_verbose_name,
                                                           ordering_html)
    else:
        header = '<th>%s</th>' % context.get('verbose_name_plural', '').capitalize()
    return u'<tr>%s</tr>' % header


@register.simple_tag(takes_context=True)
def list_item(context, list_display=None, list_display_links=None, obj=None, url=''):
    # PARAMS initialization
    if not list_display:
        list_display = context.get('list_display', [])
    if not obj:
        obj = context.get('object', None)
    if not list_display_links:
        list_display_links = context.get('list_display_links', [])
    if not url:
        url = context.get('url_object_detail', '')
    # Rendering item
    item = ''
    if obj:
        if list_display:
            if not list_display_links:
                list_display_links = list_display[0]['field']
            for field in list_display:
                attr = getattr(obj, field['field'])
                if field.get('callable', False):
                    attr = attr()
                if field.get('boolean', False):
                    if attr:
                        boolean_icon = 'icon-ok'
                        boolean_title = _('Yes')
                    else:
                        boolean_icon = 'icon-remove'
                        boolean_title = _('No')
                    attr = '<i title="%s" class="%s"></i>' % (boolean_title, boolean_icon)
                if url and field['field'] in list_display_links:
                    item += u'<td><a href="%s">%s</a></td>' % (url, attr)
                else:
                    item += u'<td>%s</td>' % attr
        else:
            # If no list_display, we display the default verbose name object
            if url:
                item = u'<td><a href="%s">%s</a></td>' % (url, obj)
            else:
                item = u'<td>%s</td>' % (obj)
    if item:
        return u'<tr>%s</tr>' % item
    return ''
