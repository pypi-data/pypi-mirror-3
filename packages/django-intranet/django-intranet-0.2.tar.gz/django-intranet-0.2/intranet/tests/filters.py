# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template import Template, Context

class FilterTest(TestCase):

    def test_phone_filter_french(self):
        c = Context({"value": "+33.952400324"})
        t = Template("{% load intranet_values_extras %}{{ value|phone }}")
        self.assertEqual(t.render(c), '09 52 40 03 24')

    def test_phone_filter_international(self):
        c = Context({"value": "+41.952400324"})
        t = Template("{% load intranet_values_extras %}{{ value|phone }}")
        self.assertEqual(t.render(c), '+41952400324')

    def test_siret_filter(self):
        c = Context({"value": "01234567890128"})
        t = Template("{% load intranet_values_extras %}{{ value|siret }}")
        self.assertEqual(t.render(c), '012 345 678 90128')

