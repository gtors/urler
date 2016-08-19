#!/usr/bin/env python

"""
A module for URL-building/parsing/manipulating.
"""

import re
import codecs
import doctest
import urllib.parse

from copy import copy
from operator import attrgetter
from collections import Iterable, OrderedDict
from .santizer import Sanitizer
from .userinfo import UserInfo
from .fragment import Fragment
from .params import Params
from .scheme import Scheme
from .host import Host
from .port import Port
from .path import Path


__all__ = ('URL',)


class URL:
    """
    A class for URL-building/parsing/manipulating.
    """
    __slots__ = (
        'scheme', 'username', 'password', 'host', 'port',
        '_inferred_port', 'path', 'params', 'query',
        'fragment', '_mutable'
    )

    def __init__(self, url, mutable=False):
        """
        >>> URL('http://example.com', path='/path').to_str()
        'http://example.com/path'
        """
        parsed = urllib.parse.urlparse(url)

        self.scheme = Scheme(parsed.scheme)
        self.host = Host(parsed.hostname)
        self.port = Port(parsed.port)
        self.path = Path(parsed.path)
        self.params = Params(parsed.params)
        self.query = Params(parsed.query)
        self.fragment = Fragment(parsed.fragment)
        self.userinfo = UserInfo(parsed.username, parsed.password)

        self._mutable = mutable
        self.port._infer_by_scheme(self.scheme.to_str())

    def __copy__(self):
        return self.__class__(self.to_str())

    def __eq__(self, other):
        """
        >>> URL('http://example.com') == 'http://example.com:80/'
        True
        """
        if isinstance(other, str):
            _other = self.__class__(other)
        elif isinstance(other, self.__class__):
            _other = copy(other)
        else:
            return False

        _self = self.__generalize(copy(self))
        _other = self.__generalize(_other)

        attrs = [
            attrgetter(attr)
            for attr in (
                'username', 'password',
                'scheme', 'host', '_inferred_port',
                'path', 'params', 'query',
                'fragment'
            )
        ]

        return all(attr(_self) == attr(_other) for attr in attrs)

    @staticmethod
    def __generalize(url):
        url.sort_query()
        url.sort_params()
        url.remove_frag()
        url.add_path('/')
        url.abspath()
        url.escape()
        url.punycode()
        return url

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        netloc = self.userinfo + self.host + self.port
        query = self.query.to_str()
        params = self.params.to_str().replace('&', ';')

        return urllib.parse.urlunparse((
            self.scheme, netloc,
            self.path, params, query,
            self.fragment))

    def __repr__(self):
        return '<urler.URL object "{}">'.format(self.to_str())

    def mutable():
        self._mutable = True

    def immutable():
        self._mutable = False

    def is_absolute(self):
        """
        Return True if this is a fully-qualified URL with a hostname
        and everything.

        >>> Host('example.com/').is_absolute()
        True
        >>> Host('/').is_absolute()
        False
        """
        return bool(self.host)

    def to_str(self):
        """
        Return a unicode version of this url.
        """
        return str(self)


if __name__ == "__main__":
    doctest.testmod()
