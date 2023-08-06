# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from intranet.views import (DashboardView)
from intranet.forms import LoginIntranetForm, PasswordChangeIntranetForm


urlpatterns = patterns('',

                       # Dashboard
                       url(r'^dashboard/$', login_required(DashboardView.as_view()), name="dashboard"),

                       # Log In/Out URLs
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login',
                           {'template_name': 'intranet/registration/login.html',
                            'authentication_form': LoginIntranetForm,},
                           name="login"),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login',
                           name="logout"),
                       url(r'^accounts/password/change/$', 'django.contrib.auth.views.password_change',
                           {'template_name': 'intranet/registration/password_change.html',
                            'password_change_form' : PasswordChangeIntranetForm,
                            'post_change_redirect': settings.PASSWORD_CHANGE_REDIRECT_URL,
                            'extra_context': {'cancel_url': settings.PASSWORD_CHANGE_REDIRECT_URL}},
                           name="password-change"),

                       )
