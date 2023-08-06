#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import urlparse
try:
    import json
except ImportError:
    import simplejson as json


def normalize_api_url(url):
    """
    >>> normalize_api_url('abc')
    'http://abc:8006/api2/json'

    >>> normalize_api_url('abc/cde')
    'http://abc:8006/cde'

    >>> normalize_api_url('https://abc:333/cde')
    'https://abc:333/cde'
    """

    scheme, netloc, path, params, query, frag = urlparse.urlparse(url)
    if not scheme:
        scheme = 'https'
        try:
            netloc, path = path.split('/', 1)
        except ValueError:
            netloc, path = path, ''
    if ':' not in netloc:
        netloc += ':8006'
    if not path:
        path = '/api2/json'
    return urlparse.urlunparse((scheme, netloc, path, params, query, frag))


class MethodRequest(urllib2.Request):
    def __init__(self, method=None, *args, **kwargs):
        urllib2.Request.__init__(self, *args, **kwargs)
        self.method = method

    def get_method(self):
        if self.method is None:
            return urllib2.Request.get_method(self)
        return self.method


class PVE2(object):
    def __init__(self, url, user, password, realm='pam'):
        self.url = normalize_api_url(url)
        self.user = user
        self.realm = realm
        self.ticket, self.csrf = self.get_login_data(user, password, realm)

    def get_login_data(self, user, password, realm):
        url = '/'.join([self.url, 'access', 'ticket'])
        data = urllib.urlopen(url, data=urllib.urlencode({
            'username': '%s@%s' % (user, realm),
            'password': password,
        })).read()
        reply = json.loads(data)
        return reply['data']['ticket'], reply['data']['CSRFPreventionToken']

    def relogin(self):
        self.ticket, self.csrf = self.get_login_data(self.user, self.ticket,
                                                     self.realm)

    def _send_request(self, url, data=None, method=None):
        request = MethodRequest(method, url, data)
        request.add_header('CSRFPreventionToken', self.csrf)
        request.add_header('Cookie', urllib.urlencode({
            'PVEAuthCookie': self.ticket,
        }))
        try:
            data = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            if getattr(e, 'status', None) == 401:
                self.relogin()
                request.add_header('CSRFPreventionToken', self.csrf)
                request.add_header('Cookie', urllib.urlencode({
                    'PVEAuthCookie': self.ticket,
                }))
                data = urllib2.urlopen(request).read()
            else:
                raise
        reply = json.loads(data)
        return reply['data']

    def GET(self, *args, **kwargs):
        url = '/'.join((self.url,) + args)
        query = urllib.urlencode(kwargs)
        if query:
            url += '?' + query
        return self._send_request(url)

    def POST(self, *args, **kwargs):
        url = '/'.join((self.url,) + args)
        post = urllib.urlencode(kwargs)
        return self._send_request(url, post)

    def PUT(self, *args, **kwargs):
        url = '/'.join((self.url,) + args)
        post = urllib.urlencode(kwargs)
        return self._send_request(url, post, method='PUT')

    def DELETE(self, *args, **kwargs):
        url = '/'.join((self.url,) + args)
        query = urllib.urlencode(kwargs)
        if query:
            url += '?' + query
        return self._send_request(url, method='DELETE')

