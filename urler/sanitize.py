from .decorators import delegate

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

# TODO: need rework
class Sanitize:

    def sanitize(self):
        """
        A shortcut to abspath and escape.
        """
        return self.abspath().escape()

    @staticmethod
    def percent_encode(raw, safe_chars):
        """
        >>> URL.percent_encode('привет мир!', safe=[])
        'a'
        """
        def replacement(match):
            raw_char = match.group(1)
            if len(raw_char) == 1:
                return raw_char if raw_char in safe_chars else '%{:02X}'.format(ord(raw_char))
            else:
                # Replace any escaped entities with their equivalent if needed.
                char = chr(int(match.group(2), 16))
                if (char in safe_chars) and (char not in URL.RESERVED):
                    return char
                return raw_char.upper()
        return URL.PERCENT_ESCAPING_RE.sub(replacement, raw)

    @delegate
    def escape(self):
        """
        Make sure that the path is correctly escaped.
        """
        self.path = self.percent_encode(self.path, URL.PATH)
        self.username = self.percent_encode(self.username, URL.USERINFO)
        self.password = self.percent_encode(self.password, URL.USERINFO)

        _query = self.percent_encode(self.query.to_str(), URL.QUERY)
        self.query = _Params(_query)

        _params = self.percent_encode(self.params.to_str(), URL.QUERY)
        self.params = _Params(_params)

        return self

    @delegate
    def unescape(self):
        """
        Unescape the path.
        """
        self.path = urllib.parse.unquote(self.path)
        self.query = _Params(urllib.parse.unquote(self.query.to_str()))
        self.params = _Params(urllib.parse.unquote(self.params.to_str()))
        self.username = urllib.parse.unquote(self.username)
        self.password = urllib.parse.unquote(self.password)
        return self
