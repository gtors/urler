import doctest
from .decorators import delegate


class Path:

    __slots__ = ('path')

    def __init__(self, path=None):
        self.path = path

    def __str__(self):
        return str(self.path or '')

    def __repr__(self):
        return '<urler.Path object "{}">'.format(self.to_str())

    def __bool__(self):
        return bool(self.path)

    def __copy__(self):
        return self.__class__(self.path)

    @delegate
    def abspath(self):
        """
        Clear out any '..' and excessive slashes from the path.

        >>> p = Path('/a///////b///1/../c/d')
        >>> p.abspath()
        >>> p.to_str()
        '/a/b/c/d'
        """
        if not self.path.endswith('/'):
            self.path = urllib.parse.urljoin(self.path + '/', '.').rstrip('/')
        else:
            self.path = urllib.parse.urljoin(self.path, '.')
        return self

    @delegate
    def set_path(self, path, append=False):
        """
        >>> p = Path(None, '/a')
        >>> p.set_path('/b')
        >>> p.to_str()
        '/b'
        >>> p.set_path('/c', append=True)
        >>> p.to_str()
        '/b/c'
        """
        if append:
            self.path = '/'.join((self.path.rstrip('/'), path.lstrip('/')))
        else:
            self.path = path
        return self

    def to_str(self):
        return str(self)


if __name__ == '__main__':
    doctest.testmod()
