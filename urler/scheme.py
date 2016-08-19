import doctest
from .decorators import delegate_properties, delegate_terminator


SECURE_SCHEMES = ('https', 'ssh', 'ftps')


@delegate_properties('scheme')
class Scheme:

    __slots__ = ('scheme')

    def __init__(self, scheme):
        self.scheme = None
        self.set(scheme)

    def __str__(self):
        return self.scheme or ''

    def __repr__(self):
        return '<urler.Scheme object {}>'.format(self.scheme)

    def __bool__(self):
        return self.scheme is not None

    def __copy__(self):
        return self.__class__(self.scheme)

    def to_str(self):
        return str(self)

    @delegate_terminator
    def is_secure(self):
        return self.scheme in SECURE_SCHEMES


if __name__ == '__main__':
    doctest.testmod()
