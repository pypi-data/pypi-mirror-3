# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from intranet.base_forms import IntranetForm, IntranetModelForm


class LoginIntranetForm(IntranetForm, AuthenticationForm):
    pass

class PasswordChangeIntranetForm(IntranetForm, PasswordChangeForm):
    
    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeIntranetForm, self).__init__(user, *args, **kwargs)
