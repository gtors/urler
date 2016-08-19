import doctest
from publicsuffixlist import PublicSuffixList
from .decorators import delegate, delegate_terminator

PSL = PublicSuffixList()
IDNA = codecs.lookup('idna')


class Host:

    __slots__ = ('host')

    def __init__(self,host=None):
        self.host = None
        self.set_host(host)

    def __str__(self):
        return self.host

    def __repr__(self):
        return '<urler.Host object {}>'.format(str(self))

    def __bool__(self):
        """
        >>> bool(Host())
        False
        >>> bool(Host('example.com'))
        True
        """
        return bool(self.host)

    def __copy__(self):
        return self.__class__(self.host)

    @delegate('set_host')
    def set(self, host):
        """
        >>> h = Host()
        >>> h.set_host('.a.com')
        >>> h.to_str()
        'a.com'
        """
        self.host = host and host.strip('.')

    @delegate
    def set_subdomain(self, subdomain, append=False):
        """
        >>> h = Host('example.com')
        >>> h.set_subdomain('test')
        >>> h.to_str()
        'test.example.com'
        >>> h.set_subdomain('a', append=True)
        >>> h.to_str()
        'a.test.example.com'
        """
        self.host = '.'.join((subdomain.strip('.'), self.pld if append else self.host))

    @delegate
    def set_domain(self, domain):
        """
        >>> h = Host('test.example.com')
        >>> h.set_domain('a')
        >>> h.to_str()
        'test.a.com'
        """
        self.host = '.'.join((self.subdomain, domain.strip('.'), self.tld))

    @delegate
    def set_pld(self, pld):
        """
        >>> h.Host('test.example.com')
        >>> h.set_pld('a.net')
        >>> h.to_str()
        'test.a.net'
        """
        self.host = '.'.join((self.subdomain(), pld.strip('.')))

    @delegate
    def set_tld(self, tld):
        """
        >>> h = Host('example.com')
        >>> h.set_tld('ru')
        >>> h.to_str()
        'example.ru'
        """
        self.host = self.host[:-len(self.tld)] + tld.strip('.')

    @delegate
    @property
    def subdomain(self):
        """
        Return the subdomain of the host.

        >>> Host('ru.example.com').subdomain
        'ru'
        """
        return self.host and self.host[:-len(self.pld)].strip('.') or ''

    @delegate_terminator
    @property
    def domain(self):
        """
        Return the domain of the host.

        >>> Host('ru.example.com').domain
        'example'
        """
        return self.host and self.pld[:-len(self.tld)].strip('.') or ''

    @delegate_terminator
    @property
    def pld(self):
        """
        Return the pay-level domain of the host.

        >>> Host('ru.example.com').pld
        'example.com'
        """
        return self.host and PSL.privatesuffix(self.host) or ''

    @delegate_terminator
    @property
    def tld(self):
        """
        Return the top-level domain of a host.

        >>> Host('example.com').tld
        'com'
        """
        return self.host and PSL.publicsuffix(self.host) or ''

    @delegate
    def punycode(self):
        """
        Convert to punycode hostname.
        See https://tools.ietf.org/html/rfc3492.

        >>> h = Host('кремль.рф')
        >>> h.punycode()
        >>> h.to_str()
        'xn--e1ajeds9e.xn--p1ai'
        """
        if not self.host:
            raise TypeError('Cannot punycode a relative URL {}'.format(repr(self)))
        self.host = IDNA.encode(self.host)[0].decode('utf-8')

    @delegate
    def unpunycode(self):
        """
        Convert to an unpunycoded hostname.

        >>> h = Host('xn--e1ajeds9e.xn--p1ai')
        >>> h.unpunycode()
        >>> h.to_str()
        'кремль.рф'
        """
        if not self.host:
            raise TypeError('Cannot unpunycode a relative url {}'.format(repr(self)))
        self.host = IDNA.decode(self.host.encode('utf-8'))[0]


if __name__ == '__main__':
    doctest.testmod()
