import doctest


@delegate_properties('username', 'password')
class UserInfo:

    __slots__ = ('username', 'password')

    def __init__(self, username=None, password=None):
        self.username = username or None
        self.password = password or None

    def __str__(self):
        return "{}:{}".format(
            self.username or '',
            self.username and self.password or ''
        ).strip(':')

    def __repr__(self):
        return '<urler.UserInfo object {}>'.format(str(self))

    def __bool__(self):
        """
        >>> bool(UserInfo())
        False
        >>> bool(UserInfo(username='name'))
        True
        """
        return bool(self.username)

    def to_str(self):
        return str(self)


if __name__ == '__main__':
    doctest.testmod()
