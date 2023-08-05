# -*- coding: utf-8 -*-
"""
    test_base
    ~~~~~~~~~

    A way of faking out FluidDB in fom, for testing.

    :copyright: (c) 2010 by AUTHOR.
    :license: MIT, see LICENSE_FILE for more details.
"""

from collections import deque


from fom.db import FluidDB, _generate_endpoint_url


class FakeHttpLibResponse(dict):

    def __init__(self, status, content_type):
        # yeah, I know, blame httplib2 for this API
        self.status = status
        self['content-type'] = content_type


class FakeHttpLibRequest(object):

    def __init__(self, response):
        self.response = response

    def __call__(self, *args):
        self.args = args
        return self.response


class FakeFluidDB(FluidDB):

    def __init__(self):
        FluidDB.__init__(self, 'http://testing')
        self.reqs = []
        self.resps = deque()
        self.default_response = (
            FakeHttpLibResponse(200, 'text/plain'), 'empty')

    def add_resp(self, status, content_type, content):
        hresp = FakeHttpLibResponse(status, content_type)
        self.resps.append((hresp, content))

    def _build_request(self, method, path, payload, urlargs, content_type):
        path = _generate_endpoint_url('', path, '')
        req = (method, path, payload, urlargs, content_type)
        self.reqs.append(req)
        try:
            resp = self.resps.popleft()
        except IndexError:
            resp = self.default_response
        return FakeHttpLibRequest(resp), (method, path, payload, urlargs,
            content_type)
