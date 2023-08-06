# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User

from intranet.tests import HOST_SERVER_TEST, default_login_with_user

class LoginTest(TestCase):

    fixtures = ['intranet_users.yaml']

    def setUp(self):
        # User Admin : superuser
        self.user_admin = User.objects.get(username='admin')
        # User 0 : all rights (e.g. 'permanent' )
        self.user_0 = User.objects.get(username='user0')
        # User 1 : no rights
        self.user_1 = User.objects.get(username='user1')
        # User 2 : no rights
        self.user_2 = User.objects.get(username='user2')
        # User 3 : no rights
        self.user_3 = User.objects.get(username='user3')
        # User 4 : no rights
        self.user_4 = User.objects.get(username='user4')


    def test_login_required_view_with_anonymous_user(self):
        """
        Test a simple login required view with an non loged user.

        We get a 302 status code response and redirect to the login url.
        """
        url = reverse('intranet:dashboard')
        response = self.client.get(url, follow=True)
        # We check redirection to login page
        expected_url = u'%s%s?next=%s' % (HOST_SERVER_TEST, settings.LOGIN_URL, url)
        self.assertRedirects(response, expected_url)


    def test_login_required_view_with_loged_superuser(self):
        """
        Test a simple login required view with an loged superuser.

        We get a 200 status code response and the dashboard view.
        """
        url = reverse('intranet:dashboard')
        # Authentication of user
        is_authorized = default_login_with_user(self.client, self.user_admin)
        self.assertEqual(is_authorized, True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_required_view_with_loged_user(self):
        """
        Test a simple login required view with an loged user (no superuser).

        We get a 200 status code response and the dashboard view.
        """
        # Authentication of entrepreneur
        url = reverse('intranet:dashboard')
        # Authentication of user
        is_authorized = default_login_with_user(self.client, self.user_0)
        self.assertEqual(is_authorized, True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
