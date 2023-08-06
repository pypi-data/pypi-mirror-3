# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name="intranet/dashboard.html"
