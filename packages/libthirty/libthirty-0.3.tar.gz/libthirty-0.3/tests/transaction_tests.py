from nose.tools import *
from mock import patch

from httplib2 import Response
from libthirty.http import Transaction
from libthirty import Authenticate
from libthirty.state import env


@patch('httplib2.Http.request')
def test_a_http_transaction(mock_request):
    """Make a http request and evaluate the response."""
    response = Response({})
    mock_request.return_value = (response, '')

    env.auth = Authenticate('testuser', 'testpassword', '30loops',
                                    auth_type='basic')
    # If the authentication succeeds, the is_authenticated flag must be set to

    t = Transaction('/path/', 'GET')
    resp, content = t.emit()
    # Make sure the the request has been really made
    assert mock_request.called
