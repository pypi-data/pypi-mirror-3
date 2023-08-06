# coding: utf-8

import simplejson
import oauth2

class ViadeoConnector(object):
    apiurl = "https://api.viadeo.com"

    def __init__(self, key, secret, token):
        self.token = token
        consumer = oauth2.Consumer(key=key, secret=secret)
        self.client = oauth2.Client(consumer)

    def __apiurl(self, endpoint, **kwargs):
        url = "%s/%s?access_token=%s" % (self.apiurl, endpoint, self.token)
        for k, v in kwargs.iteritems():
            url += "&%s=%s" % (k, v)
        return url

    def profile(self):
        resp, content = self.client.request(self.__apiurl("me", connections="career"), "GET")
        # FIXME: error handling
        return simplejson.loads(content)

    def educations(self):
        resp, content = self.client.request(self.__apiurl("me/education"), "GET")
        # FIXME: error handling
        return simplejson.loads(content)

    def tags(self):
        resp, content = self.client.request(self.__apiurl("me/tags"), "GET")
        return simplejson.loads(content)
