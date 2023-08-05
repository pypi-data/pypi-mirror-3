import httplib2 as http

from .state import env
from .http import Transaction
from .exceptions import NotAuthenticatedError

try:
    import simplejson as json
except ImportError:
    import json


class Account(object):
    """Create a representation of a remote resource that exposes all necessary
    attributes and operations to manipulate the resource. It basically wraps a
    HTTP call and constructs from the JSON representation that gets retrieved a
    object. The object exposes also CRUD operations and all possible actions.

    :param str label: The type of the resource.
    :param str name: The name of the resource.

    """
    def __init__(self):
        if not 'auth' in env:
            raise NotAuthenticatedError

        if not env.auth.is_authenticated:
            raise NotAuthenticatedError

        t = Transaction('/%s/' % env.auth.account, 'GET')
        resp, content = t.emit()

#        resource = json.loads(content)

#        self.rid = {'name': resource['name'], 'label': resource['label'], 'account':
#                    env.auth.account}
#        self.variant = resource['variant']
#        self.state_fields = []
#        for k, v in resource['state'].iteritems():
#            self.state_fields.append(k)
#            setattr(self, k, v)
