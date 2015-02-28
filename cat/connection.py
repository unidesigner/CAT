# Script initially by Tom Kazimiers 2013-01-12
# Adapted by Albert Cardona 2013-01-25
# Adapted by Stephan Gerhard 2015-02-28
#
# The purpose of this script is to connect to a django session
# in a remote computer, and to retrieve information from the database
# such as the skeleton of a neuronal arbor and its synapses
# in the form of a NetworX graph.

import urllib
import urllib2
import base64
import cookielib
import sys
import json
from collections import defaultdict

class Connection:
    def __init__(self, server, username, password, project_id, authname=None, authpassword=None ):
        self.server = server
        self.authname = authname
        self.authpassword = authpassword
        self.username = username
        self.password = password
        self.project_id = project_id
        self.cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor(self.cookies))

    def djangourl(self, path):
        """ Expects the path to lead with a slash '/'. """
        return self.server + path

    def auth(self, request):
        if self.authname:
            base64string = base64.encodestring('%s:%s' % (self.authname, self.authpassword)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

    def login(self, neurocity=False):
        if neurocity:
            accounts_url = "/accounts/catmaid/login"
        else:
            accounts_url = "/accounts/login"
        url = self.djangourl( accounts_url )
        opts = {
            'name': self.username,
            'pwd': self.password
        }
        data = urllib.urlencode(opts)
        request = urllib2.Request(url, data)
        if not self.authname is None:
            self.auth(request)
        response = urllib2.urlopen(request)
        self.cookies.extract_cookies(response, request)
        return response.read()

    def _fetch(self, url, post=None):
        """ Requires the url to connect to and the variables for POST, if any, in a dictionary. """
        if post:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url)

        self.auth(request)
        return self.opener.open(request).read()

    def fetch(self, url, post=None):
        if self.project_id is None:
            raise("Need to provide a valid project ID before calling the CATMAID API")
        requesturl = self.djangourl('/{0}/'.format( self.project_id ) + url)
        return self.fetchJSON( requesturl, post )

    def fetchJSON(self, url, post=None):
        if isinstance(post, dict):
            response = self._fetch(url, post=urllib.urlencode(post))
        else:
            response = self._fetch(url, post=post)
        if not response:
            return
        r = json.loads(response)
        if type(r) == dict and 'error' in r:
            print "ERROR:", r['error']
        else:
            return r