# -*- coding: utf-8 -*-
'''
Created on 22.06.2012

@author: Jan Brohl <janbrohl@t-online.de>
@license: Simplified BSD License see license.txt
@copyright: Copyright (c) 2012, Jan Brohl <janbrohl@t-online.de>. All rights reserved.
'''
from urlparse import urljoin
from urllib import quote, urlencode
from simplerest.util import geturl, default_hook, CallableVirtualPath
from simplerest import __version__ as ver
import sys
try:
    from json import dumps, loads, JSONDecoder
except:
    from simplejson  import dumps, loads, JSONDecoder


class REST(object):
    agentstring = "simplerest/%s (%s)" % (ver, sys.version)
    def __init__(self, basispfad, media_types=["*/*"]):
        self.basispfad = basispfad
        self.media_types = media_types

    def get(self, objektpfad, **query_args):
        """
        abrufen eines objektpfades und deserialisieren der antwort
        """
        if query_args:
            objektpfad = objektpfad + "?" + urlencode(query_args)
        s = geturl(urljoin(self.basispfad, objektpfad),
                   headers={"Accept": ", ".join(self.media_types), "User-Agent":self.agentstring})
        obj = self.load(s)
        if isinstance(obj, Exception):
            raise obj
        return obj

    def virtual_path(self):
        return CallableVirtualPath(oncall=(lambda path, query_args:
                                   self.get("/".join(path), **query_args)))

    def __repr__(self):
        return "%s(%r,%r)" % (self.__class__.__name__, self.basispfad, self.media_types)


class JSON_REST(REST):
    def __init__(self, basispfad, object_hook=default_hook):
        REST.__init__(self, basispfad, ["application/json"])
        self.object_hook = object_hook

    def load(self, s):
        return loads(s, object_hook=self.object_hook)

    def get(self, objektpfad, **query_args):
        return REST.get(self, objektpfad,
                        **dict((k, dumps(v)) for k, v in query_args.items()))

    def __repr__(self):
        return "%s(%r,%r)" % (self.__class__.__name__, self.basispfad, self.object_hook)
