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
from libthirty import Resource
from libthirty import env
from libthirty.exceptions import NotAuthenticatedError


def test_not_authenticated_resource_request():
    # Retrieve resource without authentication
    assert_raises(NotAuthenticatedError, Resource, 'repository', 'thirtyloops')

    # Retrieve resource with invalid authentication
    env.auth = Mock(spec=Authenticate)
    env.auth.is_authenticated = False
    assert_raises(NotAuthenticatedError, Resource, 'repository', 'thirtyloops')


@patch.object(httplib2.Http, 'request')
def test_retrieval_of_a_repository_resource(mock_request):
    env.auth = Mock(spec=Authenticate)
    env.auth.user = 'crito'
    env.auth.password = 'password'
    env.auth.account = '30loops'

    resource_json = { "name": "thirtyloops", "label": "repository", "variant": "git",
        "state": {
            "location": "git.30loops.net",
            "user": "gitosis",
            "password": "password",
        }
    }
    c = json.dumps(resource_json)
    response = httplib2.Response({})
    mock_request.return_value = (response, c)
    res = Resource('repository', 'thirtyloops')

    mock_request.assert_called_with(
        'https://api.30loops.net/30loops/repository/thirtyloops/',
        'GET', '',
        {'Accept': 'application/json','Content-Type':
                 'application/json; charset=UTF-8'},
    )

    eq_("git.30loops.net", res.location)
    eq_("gitosis", res.user)
    eq_("password", res.password)
    eq_({'account': '30loops', 'name': 'thirtyloops', 'label':'repository'},
        res.rid)
    assert_items_equal(['location', 'user', 'password'], res.state_fields)
