#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""End-to-end test using gaedriver.

Test environment
================

This test modules expects to find both, 'unittest2' and 'gaedriver',
in sys.path.  Also the gaedriver configuration is looked up in
'$HOME/.gaedriver'.


Configuration
=============

To run this test, copy '.gaedriver' to your $HOME directory and
set the attributes accordingly.

A possible dev_appserver configuration:
'''
[config]
app_id: my-test-app-id
cluster_hostname: localhost:8080
sdk_dir: /PATH/TO/SDK/
app_dir: /PATH/TO/gaedriver/py/demo/app
'''

A possible appserver configuration:
'''
[config]
app_id: my-test-app-id
cluster_hostname: appspot.com
sdk_dir: /PATH/TO/SDK/
app_dir: /PATH/TO/gaedriver/py/demo/app
username: alice@example.com
password: secret
'''
"""

# pylint: disable-msg=C0111,C0103,W0232,W0603,E1101,F0401

import urllib2
import os

# We are using unittest2 because it has module-level fixtures.
import unittest2

import gaedriver

# Path to the configuration file.
TEST_CONFIG_FILE = '%s/.gaedriver' % os.environ['HOME']
# Token returned by gaedriver for started apps.
GAEDRIVER_APP_TOKEN = None


def setUpModule():
    global GAEDRIVER_APP_TOKEN
    config = gaedriver.load_config_from_file(TEST_CONFIG_FILE)
    # gaedriver.setup_app() will either deploy the app referenced in
    # config or start it with dev_appserver. The particular action
    # depends on the cluster_hostname attribute. If it points to
    # localhost (e.g., localhost:8080), dev_appserver is used. Any other
    # value will trigger a deployment.
    GAEDRIVER_APP_TOKEN = gaedriver.setup_app(config)
    print 'setUp'

def tearDownModule():
    config = gaedriver.load_config_from_file(TEST_CONFIG_FILE)
    # Once the tests are completed, use gaedriver.teardown_app() to
    # clean up. For apps started with dev_appserver, this will stop
    # the dev_appserver. For deployed apps, this is currently a NOP.
    gaedriver.teardown_app(config, GAEDRIVER_APP_TOKEN)


class AppTest(unittest2.TestCase):
    """Basic application tests."""

    def setUp(self):
        self.config = gaedriver.load_config_from_file(TEST_CONFIG_FILE)

    def test_homepage(self):
        url = 'http://%s/' % self.config.app_hostname
        response = urllib2.urlopen(url)
        self.assertEqual('Hello World', response.read())


class ETagsTest(unittest2.TestCase):
    """Test that ETag headers are served correctly."""

    def setUp(self):
        self.config = gaedriver.load_config_from_file(TEST_CONFIG_FILE)

    def test_dynamic_content(self):
        url = 'http://%s/' % (self.config.app_hostname)
        response = urllib2.urlopen(url)
        self.assertFalse('ETag' in response.headers)

    def test_static_content(self):
        url = 'http://%s/static/static.txt' % self.config.app_hostname
        response = urllib2.urlopen(url)
        self.assertTrue('ETag' in response.headers)
