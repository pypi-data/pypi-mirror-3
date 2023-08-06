# -*- coding: utf-8 -*-
'''
Created on 23.06.2012

@warning: almost untested

@author: Jan Brohl <janbrohl@t-online.de>
@license: Simplified BSD License see license.txt
@copyright: Copyright (c) 2012, Jan Brohl <janbrohl@t-online.de>. All rights reserved.
'''

from wsgiref.simple_server import make_server
from wsgiref.util import request_uri
from json import dumps, load
from urlparse import urlsplit, parse_qs
statuscodes = {200:"OK", 404:"Not Found", 500:"Internal Server Error", 415:"Unsupported Media Type", 201:"Created", 204:"No Content", 501:"Not Implemented"}


def rc(code):
    return "%i %s" % (code, statuscodes[code])

class App(object):
    def __init__(self, root):
        self.root = root

    def find(self, path):
        obj = self.root
        for p in path:
            try:
                obj = obj[p]
            except:
                try:
                    obj = obj[int(p)]
                except:
                    raise KeyError(p)

    def response_obj(self, start_response, code, parsed, obj):
        try:
            ret = dumps(obj)
        except:
            return self.response_text(start_response, 500, '"%s" could not serialized' % parsed.geturl())
        headers = [("Content-Type", "application/json; charset=UTF-8"), ("content-length", str(len(ret)))]
        start_response(rc(code), headers)
        return [ret]

    def response_empty(self, start_response, code, headers=[]):
        start_response(rc(code), headers)
        return []

    def response_text(self, start_response, code, text):
        start_response(rc(code), [("Content-Type", "text/plain; charset=UTF-8"), ("content-length", str(len(text)))])
        return [text]

    def __call__(self, environ, start_response):
        parsed = urlsplit(request_uri(environ))
        url = parsed.path.strip("/")
        #query = parse_qs(environ["QUERY_STRING"], keep_blank_values=True)
        if url:
            path = url.split("/")
        else:
            path = []
        method = environ["REQUEST_METHOD"]
        if method == "GET" or method == "HEAD":
            try:
                obj = self.find(path)
            except KeyError, e:
                self.response_text(415, '"%s" could not be mapped to an object' % parsed.geturl())
            self.response_obj(start_response, 200, parsed, obj)
        elif method == "DELETE":
            obj = self.find(path[:-1])
            obj = obj.pop(path[-1])
            self.response_obj(start_response, 200, parsed, obj)
        elif method == "PUT":
            if not environ["HTTP_Content-Type"].startswith("application/json"):
                return self.response_text(start_response, 415, 'only "application/json" supported for put')
            value = load(environ["wsgi.input"])
            try:
                obj = self.find(path[:-1])
            except KeyError, e:
                self.response_text(415, '"%s" could not be mapped to an object' % parsed.geturl())
            name = path[-1]
            if name in obj:
                obj[name] = value
                return self.response_empty(start_response, 204)
            else:
                obj[name] = value
                return self.response_empty(start_response, 201)
        else:
            self.response_text(start_response, 501, 'Sorry, "%s" is not yet implemented.' % method)


def make_app_server(rootobj, host="", port=80):
    return make_server(host, port, App(rootobj))
