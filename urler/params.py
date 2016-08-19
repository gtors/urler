import doctest
import urllib.parse
from collections import OrderedDict, Iterable

from .decorators import delegate


class Params:

    __slots__ = ('_params')

    def __init__(self, params):
        self._owner = owner
        self._params = OrderedDict(urllib.parse.parse_qs(params))

    def __str__(self):
        # There used dummy function in `quote_via` param for prevent
        # encoding special chars.
        return urllib.parse.urlencode(self._params,
                                      doseq=True,
                                      quote_via=lambda a, *_: a)

    def __repr__(self):
        return '<urler.Params object {}>'.format(self._params)

    def __copy__(self):
        return self.__class__(self.to_str())

    def __eq__(self, other):
        if isinstance(other, str):
            _other = self.__class__(other)
        elif isinstance(other, self.__class__):
            _other = copy(other)
        else:
            return False

        _self = copy(self)
        _self.sort()
        _other.sort()

        return _self.to_str() == _other.to_str()

    def __getitem__(self, name: str) -> tuple:
        """
        >>> p =  Params('x=1&x=2')
        >>> p['x']
        ('1', '2')
        >>> p['a']
        ()
        """
        return tuple(self._params.get(name, ()))

    def __setitem__(self, name, value):
        """
        >>> p = Params('')
        >>> p['x'] = (1,2)
        >>> p.to_str()
        'x=1&x=2'
        """
        self._params[name] = list(value) if is_collection(value) else [value]

    def __delitem__(self, name: str):
        """
        >>> p = Params('x=1')
        >>> del p['x']
        >>> p.to_str()
        ''
        """
        if name in self._params:
            del self._params[name]

    def __contains__(self, name: str):
        """
        >>> p = Params('x=1')
        >>> 'x' in p
        True
        >>> 'y' in p
        False
        """
        return name in self._params

    def __iter__(self):
        """
        >>> list(Params('x=1&x=2'))
        [('x', '1'), ('x', '2')]
        """
        return ((name, value)
                for name, values in self._params.items()
                for value in values)

    def __len__(self):
        """
        >>> len(Params('x=1&x=2&x=3&a=4'))
        4
        """
        return sum(map(len, self._params.values()))

    def __bool__(self):
        """
        >>> bool(Params(''))
        False
        >>> bool(Params('x=1'))
        True
        """
        return bool(self._params)

    def __call__(self, *args, **kwargs):
        for method in ('add', 'set', 'delete', 'filter_by'):
            getattr(self, method)(kwargs[method])

        if 'sort' in kwargs:
            sort_param = kwargs['sort'] 
            if callable(sort_param):
                self.sort(key=sort_param)
            elif sort_param:
                self.sort()

        if args == [None] and not kwargs:
            self.clear()

        if len(args) == 1 and isinstance(args[0], str):
            self._params = OrderedDict(urllib.parse.parse_qs(params))

        return self._owner

    @delegate('set_params')
    def set(self, params=None, **kwargs):
        """
        Set parameter. All the existed parameters with same name
        will be overridden.

        >>> p = Params('x=2&x=3&b=0')
        >>> p.set(x=1)
        >>> p.sort()
        >>> p.to_str()
        'b=0&x=1'
        """
        params = params or {}
        params.update(kwargs)
        for name, value in params.items():
            self[name] = value

    @delegate('add_params')
    def add(self, params=None, **kwargs):
        """
        Add one or multiple parameters.

        >>> p = Params('x=1')
        >>> p.add(x=2)
        >>> p.to_str()
        'x=1&x=2'
        """
        params = params or {}
        params.update(kwargs)
        for name, value in params.items():
            value = value if is_collection(value) else [value]
            self._params.setdefault(name, []).extend(value)

    @delegate('del_params')
    def delete(self, mixed=None, **kwargs):
        """
        Remove the provided query parameter out of the url.

        >>> p = Params('x=1&x=2')
        >>> p.delete(x=1)
        >>> p.to_str()
        'x=2'
        >>> p = Params('a=1&b=2')
        >>> p.delete(['a', 'b'])
        >>> p.to_str()
        ''
        >>> p = Params('a=1&a=2&a=3&b=2')
        >>> p.delete('a')
        >>> p.to_str()
        'b=2'
        """

        if isinstance(mixed, dict):
            mixed.update(kwargs)
            for name, value in mixed.items():
                if is_collection(name) and is_collection(value):
                    value = tuple(map(str, value))
                    self.filter_by(lambda k, v: not(k in name and v in value))

                elif is_collection(name) and value is not None:
                    value = str(value)
                    self.filter_by(lambda k, v: not(k in name and v == value))

                elif is_collection(name):
                    self.filter_by(lambda k, _: not(k in name))

                elif is_collection(value) and name is not None:
                    value = tuple(map(str, value))
                    self.filter_by(lambda k, v: not(k == name and v in value))

                elif is_collection(value):
                    value = tuple(map(str, value))
                    self.filter_by(lambda _, v: not(v in value))

                elif value is not None:
                    value = str(value)
                    self.filter_by(lambda k, v: not(k == name and v == value))

                else:
                    self.filter_by(lambda k, _: not(k == name))

        elif is_collection(mixed):
            self.delete(dict({tuple(mixed): None}, **kwargs))

        elif isinstance(mixed, str):
            self.delete(dict({mixed: None}, **kwargs))

        elif kwargs:
            self.delete(kwargs)

    @delegate('filter_params')
    def filter_by(self, predicate):
        """
        Filter params by specified predicate.

        >>> p = Params('a=1&b=2&bc=1')
        >>> p.filter_by(lambda k, v: v != '1')
        >>> p.to_str()
        'b=2'
        """
        new_params = OrderedDict()
        for name, value in self:
            if predicate(name, value):
                new_params.setdefault(name, []).append(value)
        self._params = new_params

    @delegate('sort_params')
    def sort(self, key=None):
        """
        Sorts parameters by specified predicate.

        >>> p = Params('c=3&a=1&b=2')
        >>> p.sort()
        >>> p.to_str()
        'a=1&b=2&c=3'
        """
        self._params = OrderedDict(sorted(self._params.items(), key=key))

    def to_str(self):
        return str(self)


def is_collection(value):
    return not isinstance(value, str) and isinstance(value, Iterable)


if __name__ == "__main__":
    doctest.testmod()
