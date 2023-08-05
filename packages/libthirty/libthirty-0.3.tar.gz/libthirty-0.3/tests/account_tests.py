import sys

if sys.version_info < (2,7):
    import unittest2

from nose.tools import *
from mock import patch, Mock

try:
    import simplejson as json
except ImportError:
    import json

import httplib2
from libthirty import Authenticate
from libthirty import Account
from libthirty import env
from libthirty.exceptions import NotAuthenticatedError


def test_not_authenticated_account_request():
    # Retrieve an account without authentication
    assert_raises(NotAuthenticatedError, Account)

    # Retrieve resource with invalid authentication
    env.auth = Mock(spec=Authenticate)
    env.auth.is_authenticated = False
    assert_raises(NotAuthenticatedError, Account)


