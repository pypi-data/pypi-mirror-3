# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.forms import models as model_forms

from intranet.base_views import (IntranetListView, IntranetDetailView,
                                 IntranetCreateView, IntranetUpdateView,
                                 IntranetDeleteView)
from intranet.base_forms import IntranetModelForm

import floppyforms as forms

import logging
logger = logging.getLogger(__name__)


def get_default_model_url(model,
                          form_class=None,
                          url_name=None,
                          prefix_pattern='',
                          prefix_name='',
                          list_view=IntranetListView,
                          detail_view=IntranetDetailView,
                          creation_view=IntranetCreateView,
                          update_view=IntranetUpdateView,
                          delete_view=IntranetDeleteView):

    module_name = model._meta.module_name

    # Get default FormClass for model
    # e.g. : EntrepreneurForm for Entrepreneur model.
    if not form_class:
        form_class = model_forms.modelform_factory(model, IntranetModelForm)
    # Get default URL name
    if not url_name:
        url_name = module_name

    # Generation of urlpatterns
    urlpatterns = patterns('')
    if list_view:
        urlpatterns += patterns('',
                               # List View
                               url(r'^%s%s/$' % (prefix_pattern, module_name),
                                   login_required(list_view.as_view(model=model)),
                                   name='%s%s-list' % (prefix_name,url_name)))
    if detail_view:
        urlpatterns += patterns('',
                               # Detail View
                               url(r'^%s%s/(?P<pk>\d+)/$' % (prefix_pattern, module_name),
                                   login_required(detail_view.as_view(model=model)),
                                   name="%s%s-detail" % (prefix_name, url_name)))
    if creation_view:
        view_form_class = getattr(creation_view, 'form_class', None)
        if not view_form_class:
            view_form_class = form_class

        urlpatterns += patterns('',
                               # Add View
                               url(r'^%s%s/add/$' % (prefix_pattern, module_name),
                                   login_required(creation_view.as_view(model=model,
                                                                        form_class=view_form_class)),
                                   name="%s%s-add" % (prefix_name, url_name)))
    if update_view:
        view_form_class = getattr(update_view, 'form_class', None)
        if not view_form_class:
            view_form_class = form_class

        urlpatterns += patterns('',
                               # Edit View
                               url(r'^%s%s/(?P<pk>\d+)/edit/$' % (prefix_pattern, module_name),
                                   login_required(update_view.as_view(model=model,
                                                                      form_class=view_form_class)),
                                   name="%s%s-edit" % (prefix_name, url_name)))
    if delete_view:
        urlpatterns += patterns('',
                               # Delete View
                               url(r'^%s%s/(?P<pk>\d+)/delete/$' % (prefix_pattern, module_name),
                                   login_required(delete_view.as_view(model=model)),
                                   name="%s%s-delete" % (prefix_name, url_name)))

    return urlpatterns
