from .decorators import delegate_properties

@delegate_properties('fragment')
class Fragment:

    __slots__ = ('fragment',)

    def __init__(self, fragment):
        self.fragment = fragment

    def __str__(self):
        return self.fragment or ''

    def __repr__(self):
        return '<urler.Fragment object "{}">'.format(self.to_str())

    def __bool__(self):
        return bool(self.fragment)

    def __copy__(self):
        return self.__class__(self.fragment)

    def to_str(self):
        return str(self)
