# -*- coding: utf-8 -*-
'''
Created on 16.06.2012

@author: Jan Brohl <janbrohl@t-online.de>
@license: Simplified BSD License see license.txt
@copyright: Copyright (c) 2012, Jan Brohl <janbrohl@t-online.de>. All rights reserved.
'''
from httplib import HTTPSConnection, HTTPConnection
from urlparse import urlsplit, urlunsplit
import re
import datetime
import codecs
from UserDict import DictMixin
datere = re.compile(u"(?:([0-9]{1,4})-([01]?[0-9])-([0-3]?[0-9]))$")
timere = re.compile(u"(?:([0-2]?[0-9]):([0-6]?[0-9]):([0-6]?[0-9]))$")
datetimere = re.compile(u"(?:([0-9]{1,4})-([01]?[0-9])-([0-3]?[0-9]).([0-2]?[0-9]):([0-6]?[0-9]):([0-6]?[0-9]))$")
intre = re.compile(u"(?:[+-]?0|(?:[1-9][0-9]*))$")
floatre = re.compile(u"(?:((?:[+-]?0|(?:[1-9][0-9]*))?)[.,]([0-9]+)(?:[Ee]|(?:[*]10[^])([+-]?0|(?:[1-9][0-9]*)))?)$")  #TODO: mehr formate
numstartre = re.compile(u"[+-]?[.]?[0-9]")
type_charsetre = re.compile('(?P<maintype>\\S+?)/(?P<subtype>\\S+?)(?:;\\s*charset=(?P<charset>\\S+))')

accept = dict()
try:
    accept["deflate"] = codecs.getdecoder("zlib")
except LookupError:
    pass
try:
    accept["bz2"] = codecs.getdecoder("bz2")
except LookupError:
    pass
default_headers = {"Accept-Encoding":", ".join(accept.keys()), "User-Agent":"PyREST/0.1"}


def request(url, method="GET", body=None, headers=dict()):
    """
    connect to an url and get a response-object
    """
    s = urlsplit(url)
    host = s.netloc
    if s.scheme == "https":
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    h = dict(default_headers)
    h.update(headers)
    if body is not None:
        conn.request(method, urlunsplit(("", "", s[2], s[3], s[4])), body, h)
    else:
        conn.request(method, urlunsplit(("", "", s[2], s[3], s[4])), headers=h)
    return conn.getresponse()


def decode(response):
    """
    Read response and decode response-body to unicode
    """
    length = response.getheader("content-length", None)
    encoding = response.getheader("Content-Encoding", None)
    m = type_charsetre.match(response.getheader("Content-Type"))
    charset = m.group("charset")
    if length is not None:
        s = response.read(int(length))
    else:
        s = response.read()
    if encoding in accept:
        s = accept[encoding](s)[0]
    return s.decode(charset)


def geturl(url, headers=dict()):
    """
    Read Unicode from URL
    """
    return decode(request(url, headers=headers))


def convert(s, defaultvalues=(lambda cls, match: None)):
    """
    Convert String value if possible in a safe way
    """
    if isinstance(s, basestring) and numstartre.match(s):
        try:
            m = datetimere.match(s)
            if m is not None:
                cls = datetime.datetime
                return datetime.datetime(*_to_ints(m))
            m = datere.match(s)
            if m is not None:
                cls = datetime.date
                return datetime.date(*_to_ints(m))
            m = timere.match(s)
            if m is not None:
                cls = datetime.time
                return datetime.time(*_to_ints(m))
            m = intre.match(s)
            if m is not None:
                cls = int
                return int(m.group(), 10)
            m = floatre.match(s)
            if m is not None:
                cls = float
                if len(m.groups()) == 3:
                    return float("%s.%se%s" % tuple((g or "0") for g in m.groups()))
                return float("%s.%s" % tuple((g or "0") for g in m.groups()))
        except ValueError:
            return defaultvalues(cls, m)
    return s


class ObjectHook(object):

    def __init__(self, string_hook=convert, key_hook=convert):
        self.string_hook = string_hook
        self.key_hook = key_hook

    def __call__(self, obj):
        """
        for use as object_hook in json.loads
        """
        sh = self.string_hook
        kh = self.key_hook
        stuff = dict()
        for k, v in obj.items():
            if isinstance(v, basestring):
                v = sh(v)
            elif isinstance(v, dict):
                v = self(v)
            stuff[kh(k)] = v
        return stuff

default_hook = ObjectHook()


def _to_ints(m):
    """
    Convert all groups of a match to int
    """
    return (int(g.lstrip("0") or "0") for g in m.groups())


def as_list(mapping):
    """
    Convert dict to list if possible (if mapping.keys()==range(len(mapping)))
    else return dict
    """
    try:
        return list(mapping[i] for i in range(len(mapping)))
    except (KeyError, IndexError):
        return mapping


class VirtualPath(DictMixin):
    def __init__(self, path=[], **kwargs):
        self._path = path
        self._kwargs = kwargs

    def __getitem__(self, key):
        return self.__class__(path=self._path + [key], **self._kwargs)

    def __str__(self):
        return str(self())

    @property
    def path_as_list(self):
        return list(self._path)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and all(other.kwarg(k) == v for k, v in self._kwargs.items())
                and self.path_as_list == other.path_as_list
                and other == self)

    def kwarg(self, name):
        return self._kwargs.get(name, None)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__,
                               self.path_as_list,
                               ", ".join("%r=%r" % kv for kv in self._kwargs.items()))

    def keys(self):
        return self["keys"]()()


class TALVirtualPath(VirtualPath):
    _forbidden = re.compile("[.]|(.*([/]|[|]|[?]|[\\\\]).*)+")

    def __init__(self, path=[], basepath=[], **kwargs):
        VirtualPath.__init__(self, path=path, basepath=basepath, **kwargs)

    @property
    def path_as_list(self):
        return list(self.kwarg("basepath") or []) + self._path

    def __getitem__(self, key):
        if isinstance(key, basestring) and self._forbidden.match(key):
            raise KeyError(key)
        elif key == "container":
            p = self.path_as_list
            if p:
                p = p[:-1]
            return self.__class__(path=p, **self._kwargs)
        elif key == "root":
            return self.__class__(path=[], **self._kwargs)
        else:
            return VirtualPath.__getitem__(self, key)


class CallableVirtualPath(VirtualPath):
    def __init__(self, path=[], oncall=(lambda path, kwargs:
                                        "/".join(path)), **kwargs):
        VirtualPath.__init__(self, path, oncall=oncall, **kwargs)

    def __call__(self, **kwargs):
        self.__kwargs["oncall"](self.__path, kwargs)


class NoCallWrapper(object):
    def __init__(self, virtualpath):
        self ._vp = virtualpath

    def __getitem__(self, key):
        return self.__class__(self._vp[key])

    def __str__(self):
        return str(self._vp)

    def __getattr__(self, name):
        return getattr(self._vp, name)
