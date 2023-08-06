#!/usr/bin/env python

import getpass
import os
import re
import requests
import sys
import time

try:
    import simplejson as json
except ImportError:
    import json 

class Client(object):
    def __init__(self, api_key=None, login=None, password=getpass.getpass("8tracks.com password > "),
            format_="json"):
        if not api_key:
            print "You must provide a valid API key!"
            sys.exit(1)
        elif not login:
            print "Please provide an 8tracks.com user login."
            sys.exit(1)
        else:
            self.base_url = "8tracks.com/"
            self.url_reqs = "?api_key=%s&format=%s" % (api_key,
                    format_)
            self.POST_payload = {"user_token": None}

        # get user token for authentication
        url = self._construct_url("sessions", ssl=True)
        credentials = {"login":login, "password":password.strip()}
        temp_payload = dict(self.POST_payload.items() +
                credentials.items())
        user_token = self._verify_status_code(requests.post(url,
            data=temp_payload)).get("user_token", None)

        # store user token in payload for reuse in methods that
        # require authentication
        self.POST_payload["user_token"] = user_token

    def _construct_url(self, context, args=None, kwargs=None, ssl=False):
        if args == None: args = ()
        if kwargs == None: kwargs = {}

        url_prefix = ssl and "https://" or "http://"
        full_context = context
        url_suffix = ""

        if args:
            for arg in args:
                full_context += '/%s' % str(arg)

        if kwargs:
            for key, value in kwargs.items():
                url_suffix += "&%s=%s" % (str(key), str(value))

        url = url_prefix + self.base_url + full_context + self.url_reqs + url_suffix
        return url

    def _verify_status_code(self, response):
        if response.status_code == requests.codes.ok:
            return json.loads(response.text)
        else:
            response.raise_for_status()

    def mixes(self, *args, **kwargs):
        base_context = "mixes"

        url = self._construct_url(base_context, args, kwargs)

        if re.search(r"(?:toggle_|un)?like", url):
            response = self._verify_status_code(requests.post(url,
                data=self.POST_payload))
        else:
            response = self._verify_status_code(requests.get(url))

        return response

    def sets(self, *args, **kwargs):
        base_context = "sets"

        # obtain a play token if we haven't already done so before
        # attempting to (play|skip|etc)
        if not hasattr(self, "play_token"):
            url = self._construct_url(base_context, args=("new",))
            response = self._verify_status_code(requests.post(url,
                data=self.POST_payload))
            self.play_token = response.get("play_token", None)

        # return play token if explicitly requested
        if "new" in args:
            return self.play_token
    
        context_with_token = '%s/%s' % (base_context, self.play_token)
        url = self._construct_url(context_with_token, args, kwargs)
        response = self._verify_status_code(requests.post(url,
            data=self.POST_payload))

        return response

    def users(self, *args, **kwargs):
        base_context = "users"

        url = self._construct_url(base_context, args, kwargs)

        if re.search(r"(?:toggle_|un)?follow", url):
            response = self._verify_status_code(requests.post(url,
                data=self.POST_payload))
        else:
            response = self._verify_status_code(requests.get(url))

        return response

    def reviews(self, *args, **kwargs):
        base_context = "reviews"
        
        url = self._construct_url(base_context, kwargs=kwargs)
        response = self._verify_status_code(requests.post(url,
            data=self.POST_payload))

        return response

    def tags(self, *args, **kwargs):
        base_context = "tags"

        url = self._construct_url(base_context, args, kwargs)
        response = self._verify_status_code(requests.get(url))

        return response

    def tracks(self, *args, **kwargs):
        base_context = "tracks"

        url = self._construct_url(base_context, args, kwargs)
        response = self._verify_status_code(requests.post(url,
            data=self.POST_payload))

        return response
