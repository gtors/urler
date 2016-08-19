import doctest


DEFAULT_PORTS = {
    'ftp': '21',
    'ssh': '22',
    'http': '80',
    'https': '443'
}


class Port:

    slots = ('_port', '_inferred_port')

    def __init__(self, port):
        self._port = None
        self.set(port)

    def __str__(self):
        return self._port or ''

    def __repr__(self):
        return '<urler.Port object {}>'.format(self._port)

    def __bool__(self):
        """
        >>> p = Port('8080')
        >>> bool(p)
        True
        """
        return self._port is not None

    def __copy__(self):
        return self.__class__(self._port)

    def __eq__(self, other):
        self_port = self._port or self._inferred_port
        if isinstance(other, self.__class__):
            other_port = other._port or other._inferred_port
        elif isinstance(other, str, long, int):
            other_port = str(other)
        else:
            return False

        return self_port == other_port

    def _infer_by_scheme(self, scheme):
        # Inferred port used only in case of comparsion ports.
        if not self._inferred_port:
            self._inferred_port = DEFAULT_PORTS.get(str(scheme))

    @delegate('set_port')
    def set(self, port):
        """
        >>> p = Port(None, None)
        >>> p.set('8080')
        >>> p.to_str()
        '8080'
        """
        port = port and str(port) or None
        self._port = port
        self._inferred_port = port

    def to_str(self):
        return str(self)


if __name__ == "__main__":
    doctest.testmod()
