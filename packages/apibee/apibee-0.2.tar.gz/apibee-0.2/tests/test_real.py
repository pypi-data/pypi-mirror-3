#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
from restdyn import Client, RequestFailed
import json
from time import sleep

TEST_SERVER = "http://localhost:8080"

class ClientTestCase(unittest.TestCase):

    def tearDown(self):
        sleep(2)

    def test_twitter(self):
        TwitterAPi = Client('https://api.twitter.com/1', end_resources='.json')
        res = TwitterAPi.search(q='test')
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['page'], 1)

    def test_google_search_set_persistent_params_kwargs(self):
        GoogleAPI = Client('http://ajax.googleapis.com/ajax/services')
        GoogleAPI.set_persistent_params(v="1.0")
        res = GoogleAPI.search.web(q="Earth Day")
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['responseStatus'], 200)

    def test_google_search_set_persistent_params_args(self):
        GoogleAPI = Client('http://ajax.googleapis.com/ajax/services')
        GoogleAPI.set_persistent_params({'v':"1.0"})
        res = GoogleAPI.search.web(q="Earth Day")
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['responseStatus'], 200)

    def test_google_search_set_persistent_params_bad(self):
        GoogleAPI = Client('http://ajax.googleapis.com/ajax/services')
        self.assertRaises(AssertionError, GoogleAPI.set_persistent_params, 'v=1.0')
        self.assertRaises(AssertionError, GoogleAPI.set_persistent_params, [('v', '1.0')])

    def test_end_resources(self):
        for end_resources in ['.json', '.xml', 'blah']:
            TwitterAPi = Client('https://api.twitter.com/1', end_resources=end_resources)
            url = TwitterAPi.search._get_url()
            self.assertTrue(url.endswith(end_resources))

    def test__getitem__(self):
        GoogleAPI = Client('http://ajax.googleapis.com')
        GoogleAPI.set_persistent_params(v="1.0")
        res = GoogleAPI['ajax'].services['search'].web(q="Earth Day")
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['responseStatus'], 200)

        res = GoogleAPI.ajax['services']['search']['web'](q="Earth Day")
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['responseStatus'], 200)

    def test_get_last_call(self):
        GoogleAPI = Client('http://ajax.googleapis.com/ajax/services')
        GoogleAPI.set_persistent_params({'v':"1.0"})
        res = GoogleAPI.search.web(q="Earth Day")
        self.assertEqual(res, json.loads(GoogleAPI._last_result))
        self.assertEqual(GoogleAPI._last_response.status_int, 200)

    def test_raise_error(self):
        TwitterAPi = Client('https://api.twitter.com/1', end_resources='.json')
        self.assertRaises(RequestFailed, TwitterAPi.search)

    def test_post_process_result(self):
        class CustomGoogleAPI(Client):
            def post_process_result(self, result):
                if result["responseStatus"] == 400:
                    raise RequestFailed(result['responseDetails'])
                return result

        GoogleAPI = CustomGoogleAPI('http://ajax.googleapis.com/ajax/services')
        try:
            GoogleAPI.search.web(q="toto")
            assert 0
        except RequestFailed, e:
            self.assertEqual(str(e), "invalid version")

