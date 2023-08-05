from .http import Transaction
try:
    import simplejson as json
except ImportError:
    #for python3
    import json


class Authenticate(object):
    """Create an authentication object that can be used to successfully
    authenticate succeeding transactions. Upon creation the credentials are
    used once for authentication. If they succeed, the credentials are cached
    and can be used by other objects. This reduces the amount of work for each
    following transaction.

    :param str username: The username to use for authentication.
    :param str password: The password to use for authentication.
    :param str auth_type: The type of authentication to use. Defaults to HTTP
                          basic authentication.

    >>> from libthirty import Authenticate
    >>> auth = Authenticate('user', 'pass')
    >>> auth.is_authenticated
    True

    """
    is_authenticated = False
    """If authentication succeeds, this attribute is set to True."""

    def __init__(self, username, password, account, auth_type='basic'):
        t = Transaction('/_authenticate/%s/' % account, 'GET')
        t.add_credentials(username, password)
        resp, content = t.emit()

        if resp.status == 200:
            self.user = username
            self.password = password
            self.is_authenticated = True
