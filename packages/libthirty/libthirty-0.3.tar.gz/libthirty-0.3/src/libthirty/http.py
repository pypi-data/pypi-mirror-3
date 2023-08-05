try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import httplib2 as http

from .state import env
from .exceptions import InvalidHttpMethod, TransactionNotSecure

class Transaction(object):
    """A simple synchronous HTTP transaction class. Wraps the request/response
    mechanism in single class. It abstracts a healthy set of default values in
    regard to caching and only allows https as a protocol.

    :param str path: A relative path or a URI. The scheme and location
                         defaults to https://api.30loops.net.
    :param str method: The HTTP method to use. Defaults to GET.

    """
    # All valid HTTP/1.1 methods
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE']

    # default headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    body = ''

    def __init__(self, path, method='GET'):
        # break requested location+path into the following components:
        #    scheme://netloc/path;parameters?query#fragment
        if not path.startswith('/'):
            # normalize the uri slashes
            path = '/' + path
        # overwrite the default location of the global state
        self.target = urlparse(env.uri+path)

        if not method.upper() in self.methods:
            # requested method is invalid
            raise InvalidHttpMethod
        self.method = method

        # only accept secure connections
        #if self.target.scheme not in 'https':
        #    raise TransactionNotSecure

        # FIXME: implement caching interface
        self._h = http.Http()

        # If the env dict has the auth object, add the credentials
        if 'auth' in env:
            self._h.add_credentials(env.auth.user, env.auth.password)

    def add_credentials(self, user, password):
        self._h.add_credentials(user, password)

    def add_header(self, header, value):
        self.headers[header] = value

    def emit(self):
        return self._h.request(
            self.target.geturl(),
            self.method,
            self.body,
            self.headers)

