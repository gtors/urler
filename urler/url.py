#!/usr/bin/env python

import re
import codecs
import urllib
from copy import copy
from operator import attrgetter
from collections import Iterable

# For publicsuffix utilities
from publicsuffixlist import PublicSuffixList

psl = PublicSuffixList()

IDNA = codecs.lookup('idna')

DEFAULT_PORTS = {
    'ftp': 21,
    'ssh': 22,
    'http': 80,
    'https': 443
}


class _Params:

    def __init__(self, params):
        self._params = params

    def filter_by(predicate):
        self._params = [p for p in self._params if predicate(*p)]

    def sort(self, _cmp=None):
        self._params.sort(cmp=_cmp)

    def add(self, name, value):
        if self._is_collection(value):
            for v in value:
                self._params.append((name, v))
        else:
            self._params.append((name, value))

    def set(self, name, value):
        remove_by(lambda k, _: k == name)
        if self._is_collection(value):
            for v in value:
                self._params.append((name, v))
        else:
            self._params.append((name, value))

    def remove(self, name, value=None):
        if self_is_collection(name):
            self.remove_by(lambda k, _: k in name and (value is None or v == value)
        elif self._is_collection(value):
            self.remove_by(lambda k, v: k == name and (value is None or v in value))
        else:
            self.remove_by(lambda k, v: k == name and (value is None or v == value))

    def remove_by(predicate):
        self._params = [p for p in self._params if not predicate(*p)]

    @staticmethod
    def _is_collection(value):
        return not isinstance(value, str) and isinstance(value, Iterable)


class URL:

    __slots__ = (
        'scheme', 'username', 'password', 'host', 'port',
        '_inferred_port', 'path', 'params', 'query',
        'fragment'
    )

    # From http://www.ietf.org/rfc/rfc3986.txt
    GEN_DELIMS = ":/?#[]@"
    SUB_DELIMS = "!$&'()*+,;="
    ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    DIGIT = "0123456789"
    UNRESERVED = ALPHA + DIGIT + "-._~"
    RESERVED = GEN_DELIMS + SUB_DELIMS
    PCHAR = UNRESERVED + SUB_DELIMS + ":@"
    PATH = PCHAR + "/"
    QUERY = PCHAR + "/?"
    FRAGMENT = PCHAR + "/?"
    USERINFO = UNRESERVED + SUB_DELIMS + ":"

    PERCENT_ESCAPING_RE = re.compile('(%([a-fA-F0-9]{2})|.)', re.S)

    def __init__(self, url, **kwargs):
        """
        >>> URL('http://example.com', path='/path').to_str()
        'http://example.com/path'
        """
        parsed = urllib.parse.urlparse(url)

        self.host = parsed.hostname or ''
        self.port = parsed.port or ''
        self.path = parsed.path or ''
        self.params = parsed.params or ''
        self.query = parsed.query or ''
        self.fragment = parsed.fragment or ''
        self.username = parsed.username or ''
        self.password = prsed.password or ''

        # For future comparsion
        self._inferred_port = port or scheme and DEFAULT_PORTS.get(scheme)

        if kwargs:
            self.update(**kwargs)

    def update(self, *, scheme=None, host=None, port=None, path=None,
            params=None, query=None, fragment=None, username=None, 
            password=None):
        """
        >>> URL('http://example.com').update(
        >>>    port='8080'
        >>>    path='/a/b/c'
        >>> ).to_str()
        'http://example.com:8080/a/b/c'
        """
        if username:
            self.username = username
        if password:
            self.password = password
        if scheme:
            self.scheme = scheme
        if host:
            self.host = host
        if port:
            self.port = port
        if path:
            self.path = path
        if query:
            self.query = query
        if fragment:
            self.fragment = fragment
        return self

    def __copy__(self):
        return self.__class__(self.to_str())

    def __eq__(self, other):
        """
        >>> URL('http://example.com') == 'http://example.com:80/'
        True
        """
        if isinstance(other, str):
            _other = self.parse(other, encoding)
        else:
            _other = copy(other)

        _self = copy(self)
        _self.canonical().defrag().abspath().escape().with_punycode()
        _other.canonical().defrag().abspath().escape().with_punycode()

        attrs = map(attrgetter(
            'userinfo',
            'scheme', 'host', '_inferred_port',
            'path', 'params', 'query',
            'fragment'))

        return all(attr(_self) == attr(_other) for attr in attrs)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return '<url.URL object "{}">'.format(self.to_str())

    # Scheme methods
    # ------------------------------------------------------------------------

    def set_scheme(self, scheme):
        """
        >>> URL('http://example.com').set_scheme('https').to_str()
        'https://example.com'
        """
        self.scheme = scheme
        return self

    def remove_scheme(self):
        """
        >>> URL('http://example.com').remove_scheme().to_str()
        '//example.com'
        """
        self.scheme = ''
        return self

    # Userinfo methods
    # ------------------------------------------------------------------------

    def set_username(self, name):
        """
        >>> URL('http://example.com').set_username('name').to_str()
        'http://name@example.com'
        """
        self.username = name
        return self

    def set_password(self, pass):
        """
        >>> URL('http://name@example.com').set_password('pass').to_str()
        'http://name:pass@example.com'
        """
        self.password = pass
        return self

    def remove_password(self):
        """
        >>> URL('http://name@example.com').remove_password().to_str()
        'http://name:pass@example.com'
        """
        self.password = ''
        return self

    def remove_userinfo(self):
        """
        >>> URL('http://name@example.com').remove_userinfo().to_str()
        'http://example.com'
        """
        self.username = ''
        self.password = ''
        return self

    # Host methods
    # ------------------------------------------------------------------------

    def set_host(self, host):
        """
        >>> URL('http://example.com').set_host('a.com').to_str()
        'http://a.com'
        """
        self.host = host.strip('.')
        return self

    def remove_host(self):
        """
        >>> URL('http://example.com/path').remove_host().to_str()
        'http:///path'
        """
        self.host = ''
        return self

    def add_subdomain(self, subdomain):
        """
        >>> URL('http://a.example.com').add_subdomain('test').to_str()
        'http://test.a.example.com'
        """
        self.host = '.'.join((subdomain.strip('.'), self.host))
        return self

    def set_subdomain(self, subdomain):
        """
        >>> URL('http://example.com').set_subdomain('test').to_str()
        'http://test.example.com'
        """
        self.host = '.'.join((subdomain.strip('.'), self.pld()))
        return self

    def remove_subdomain(self):
        """
        >>> URL('http://test.example.com').remove_subdomain().to_str()
        'http://example.com'
        """
        self.host = self.pld()
        return self

    def set_domain(self, domain):
        """
        >>> URL('http://test.example.com').set_domain('a').to_str()
        'http://test.a.com'
        """
        self.host = '.'.join((self.subdomain(), domain.strip('.'), self.tld()))
        return self

    def set_pld(self, pld):
        """
        >>> URL('http://test.example.com').set_pld('a.net').to_str()
        'http://test.a.com'
        """
        self.host = '.'.join((self.subdomain(), pld.strip('.')))
        return self

    def set_tld(self, tld):
        """
        >>> URL('http://example.com').set_tld('ru').to_str()
        'http://example.ru'
        """
        self.host = self.host[:-len(self.tld())] + tld.strip('.')
        return self

    def hostname(self):
        """
        Return the hostname of the url.

        >>> URL('ru.example.com').hostname()
        'ru.example.com'
        """
        return self.host

    def subdomain(self):
        """
        Return the subdomain of the url.

        >>> URL('ru.example.com').subdomain()
        'ru'
        """
        return self.host and self.host[:-len(self.pld())].strip('.') or ''

    def domain(self):
        """
        Return the domain of the url.

        >>> URL('ru.example.com').domain()
        'example'
        """
        return self.host and self.pld()[:-len(self.tld())].strip('.') or ''

    def pld(self):
        """
        Return the pay-level domain of the url.

        >>> URL('ru.example.com').pld()
        'example.com'
        """
        return self.host and psl.privatesuffix(self.host) or ''

    def tld(self):
        """
        Return the top-level domain of a url.

        >>> URL('example.com').tld()
        'com'
        """
        return self.host and psl.publicsuffix(self.host) or ''

    # Port methods
    # ------------------------------------------------------------------------

    def set_port(self, port):
        """
        >>> URL('http://example.com').set_port('8080').to_str()
        'http://example.com:8080'
        """
        self.port = port
        self._inferred_port = port
        return self

    def remove_port(self):
        """
        >>> URL('http://example.com:8080').remove_port().to_str()
        'http://example.com'
        """
        self.port = ''
        self._inferred_port = ''
        return self

    # Path methods
    # TODO: add path segments manipulation
    # ------------------------------------------------------------------------

    def abspath(self):
        """
        Clear out any '..' and excessive slashes from the path.

        >>> URL('http://example.com/a///////b///1/../c/d').abspath().to_str()
        'http://example.com/a/b/c/d'
        """
        self.path = urllib.parse.urljoin(self.path, '.')
        return self

    def set_path(self, path):
        """
        >>> URL('http://example.com/a').set_path('/b').to_str()
        'http://example.com/b'
        """
        self.path = path
        return self

    def add_path(self, path):
        """
        >>> URL('http://example.com/a').add_path('/b').to_str()
        'http://example.com/a/b'
        """
        self.path = '/'.join((self.path.rstrip('/'), path.lstrip('/')))
        return self

    def remove_path(self):
        """
        >>> URL('http://example.com/a').remove_path().to_str()
        'http://example.com'
        """
        self.path = ''
        return self

    def is_absolute(self):
        """
        Return True if this is a fully-qualified URL with a hostname
        and everything.

        >>> URL('//example.com').is_absolute()
        True
        >>> URL('/').is_absolute()
        False
        """
        return bool(self.host)

    # Query params methods
    # ------------------------------------------------------------------------

    def sort_query(self, _cmp=None):
        """
        >>> URL('http://example.com?c=3&a=1&b=2').sort_query().to_str()
        'http://example.com?a=1&b=2&c=3'
        """
        self.query.sort(_cmp)
        return self

    def set_query(self, mixed, value=None):
        """
        Add query params to this url.

        >>> URL('http://example.com?x=2&x=3&b=0').set_query('x', 1).to_str()
        'http://example.com?x=1'

        >>> (URL('http://example.com?x=2&x=3')
        >>>     .set_query({'x': '1', 'a': ['1','2']})
        >>>     .to_str())
        'http://example.com?x=1&a=1&a=2&b=0'
        """
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.query.set(*pair)
        else:
            self.query.set(mixed, value)
        return self

    def add_query(self, mixed, value):
        """
        Add query params to this url.

        >>> URL('http://example.com?x=2').set_query('x', 1).to_str()
        'http://example.com?x=1&x=2'

        >>> (URL('http://example.com?x=2&x=3')
        >>>     .set_query({'x': '1', 'b': '0'})
        >>>     .to_str())
        'http://example.com?x=1&x=2&x=3&b=0'
        """
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.query.add(*pair)
        else:
            self.query.add(name, value)
        return self

    def remove_query(self, mixed, value=None):
        """
        Remove the provided query parameter out of the url.

        >>> URL('http://example.com?x=1&x=2').remove_query('x', '1').to_str()
        'http://example.com?x=2'
        >>> URL('http://example.com?a=1&b=2').remove_query(['a', 'b']).to_str()
        'http://example.com'
        >>> URL('http://example.com?a=1&b=2').remove_query('a').to_str()
        'http://example.com?b=2'
        """
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.query.remove(*pair)
        else:
            self.query.remove(pair)
        return self

    def filter_query(self, predicate):
        """
        >>> (URL('http://example.com?a=1&b=2&bc=1')
        >>>     .filter_query(lambda k, v: v != '1')
        >>>     .to_str())
        'http://example.com?b=2'
        """
        self.query.filter_by(predicate)
        return self

    # Params methods
    # ------------------------------------------------------------------------

    def sort_params(self, _cmp=None):
        self.params.sort(_cmp)
        return self

    def set_params(self, mixed, value=None):
        """
        Add params param to this url.

        >>> URL('http://example.com/;x=2;x=3').set_params('x', 1).to_str()
        'http://example.com/;x=1'
        """
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.params.set(name, value)
        else:
            self.params.set(mixed, value)
        return self

    def add_params(self, mixed, value):
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.params.add(name, value)
        else:
            self.params.add(name, value)
        return self

    def remove_params(self, mixed, value=None):
        """
        Remove the provided params parameter out of the url.

        >>> URL('http://example.com/;x=1').remove_params('x', '1').to_str()
        'http://example.com'
        """
        if isinstance(mixed, dict):
            for pair in mixed.items():
                self.params.remove(*pair)
        else:
            self.params.remove(pair)
        return self

    def filter_params(self, predicate):
        self.params.filter_by(predicate)
        return self

    # Fragment methods
    # ------------------------------------------------------------------------

    def set_frag(self, frag):
        """
        Add the fragment to the url.

        >>> URL('http://example.com').set_frag('frag').to_str()
        'http://example.com#frag'
        """
        sefl.fragment = frag
        return self

    def remove_frag(self):
        """
        Remove the fragment from this url.

        >>> URL('http://example.com/#frag').remove_frag().to_str()
        'http://example.com'
        """
        self.fragment = ''
        return self

    # ------------------------------------------------------------------------

    def sanitize(self):
        """
        A shortcut to abspath and escape.
        """
        return self.abspath().escape()

    @staticmethod
    def percent_encode(raw, safe_chars):
        def replacement(match):
            s = match.group(1)
            if len(s) == 1:
                return s if s in safe_chars else '%{:02X}'.format(ord(s))
            else:
                # Replace any escaped entities with their equivalent if needed.
                c = chr(int(match.group(2), 16))
                if (c in safe_chars) and (c not in URL.RESERVED):
                    return c
                return s.upper()
        return URL.PERCENT_ESCAPING_RE.sub(replacement, raw)

    def escape(self, strict=False):
        """
        Make sure that the path is correctly escaped.
        """
        self.path = self.percent_encode(self.path, URL.PATH)
        self.query = self.percent_encode(self.query, URL.QUERY)
        self.params = self.percent_encode(self.params, URL.QUERY)
        self.username = self.percent_encode(self.userinfo, URL.USERINFO)
        self.password = self.percent_encode(self.password, URL.USERINFO)
        return self

    def unescape(self):
        """
        Unescape the path.
        """
        self.path = urllib.parse.unquote(self.path)
        self.query = urllib.parse.unquote(self.query)
        self.params = urllib.parse.unquote(self.params)
        self.username = urllib.parse.unquote(self.username)
        self.password = urllib.parse.unquote(self.password)
        return self

    def punycode(self):
        """
        Convert to punycode hostname.
        See https://tools.ietf.org/html/rfc3492.

        >>> URL('http://кремль.рф').punycode().to_str()
        'http://xn--e1ajeds9e.xn--p1ai'
        """
        if not self.host:
            raise TypeError('Cannot punycode a relative url {}'.format(repr(self)))
        self.host = IDNA.encode(self.host)[0].decode('utf-8')
        return self

    def unpunycode(self):
        """
        Convert to an unpunycoded hostname.

        >>> URL('http://xn--e1ajeds9e.xn--p1ai').unpunycode().to_str()
        'http://кремль.рф'
        """
        if not self.host:
            raise TypeError('Cannot unpunycode a relative url {}'.format(repr(self)))
        self.host = IDNA.decode(self.host.encode('utf-8'))[0]
        return self

    # Get a string representation. These methods can't be chained, as they
    # return strings
    # ------------------------------------------------------------------------

    def to_str(self):
        """
        Return a unicode version of this url
        """
        netloc = self._host or ''
        if self._port:
            netloc += (':' + str(self._port))

        if self._userinfo is not None:
            netloc = '{}@{}'.format(self._userinfo, netloc)

        result = urllib.parse.urlunparse((self._scheme, netloc,
            self._path, self._params, self._query,
            self._fragment))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
