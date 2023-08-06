# -*- coding: utf-8 -*-

HOST_SERVER_TEST = 'http://testserver' 

def default_login_with_user(client, user):
    return client.login(username=user.username,
                        password=user.username)

from intranet.tests.filters import *

