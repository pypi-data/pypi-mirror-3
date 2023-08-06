# -*- coding: utf-8 -*-

import os
import sys
from operator import attrgetter
from os.path import dirname, join as pathjoin, realpath
from nose.plugins.skip import SkipTest
from nose.tools import *

try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser

import rtm.rtm as RTM

# constant for test
KEY_TXT = pathjoin(dirname(realpath(__file__)), 'apikey.txt')
KEY_TXT_FORMAT = """
The format are(ConfigParser readable):
[rtm]
apikey: xxx
secret: yyy
token: zzz
"""


class TestRTM(object):

    message = {
        'skip': '\n\n'
            'Set your API key "%s" to run TestRTM for authentication\n'
            '%s' % (KEY_TXT, KEY_TXT_FORMAT),
        'cannot_read': '\n\n'
            'Cannot read "%s"\n'
            '%s' % (KEY_TXT, KEY_TXT_FORMAT),
        'no_item': '\n\n'
            'rtm.%s.%s: Cannot get response item, maybe there is no item\n',
    }

    def setup(self):
        if not os.access(KEY_TXT, os.R_OK):
            raise SkipTest(self.message['skip'])
        self.read_key_txt()
        self.rtm = RTM.createRTM(self.apikey, self.secret, self.token)

    def read_key_txt(self):
        try:
            c = RawConfigParser()
            c.read(KEY_TXT)
            self.apikey = c.get('rtm', 'apikey')
            self.secret = c.get('rtm', 'secret')
            self.token = c.get('rtm', 'token')
        except Exception as err:
            sys.stderr.write(err + "\n")
            raise SkipTest(self.message['cannot_read'])

    def assert_stat_ok(self, rsp):
        assert_equal("ok", rsp.stat)

    def assert_response(self, func, elem=None, **params):
        """assert the stat/attr(only top) of response from api"""
        if hasattr(func, "func_name"):
            func_name = func.func_name
        else:
            func_name = func.__name__
        api, method = func_name.replace('test_', '').split('_')
        elem = elem or api
        api_method = "%s.%s" % (api, method)
        rsp = attrgetter(api_method)(self.rtm)(**params)
        self.assert_stat_ok(rsp)  # response is ok

        rsp_attr = getattr(rsp, api)
        if not isinstance(rsp_attr, RTM.dottedDict):
            raise SkipTest(self.message['no_item'] % (api, method))
        attr = list(RTM.API_RESPONSE[api][method][elem].keys())[0]
        assert_true(hasattr(rsp_attr, attr))  # has item

    def test_auth_checkToken(self):
        params = {'auth_token': self.token}
        self.assert_response(self.test_auth_checkToken, **params)

    def test_contacts_getList(self):
        self.assert_response(self.test_contacts_getList)

    def test_groups_getList(self):
        self.assert_response(self.test_groups_getList)

    def test_lists_getList(self):
        self.assert_response(self.test_lists_getList)

    def test_locations_getList(self):
        self.assert_response(self.test_locations_getList)

    def test_settings_getList(self):
        self.assert_response(self.test_settings_getList)

    def test_tasks_getList(self):
        self.assert_response(self.test_tasks_getList, 'lists')

    def test_timezones_getList(self):
        self.assert_response(self.test_timezones_getList)
