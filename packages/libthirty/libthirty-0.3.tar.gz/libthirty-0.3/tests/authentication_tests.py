from nose.tools import *
from mock import patch

from httplib2 import Response
from libthirty import Authenticate
from libthirty.state import env


@patch('httplib2.Http.request')
def test_a_valid_authentication(mock_request):
    """Create a successfull authentication object."""
    if env.has_key('auth'):
        del(env['auth'])
    response = Response({'status': 200})
    mock_request.return_value = (response, '')
    auth = Authenticate('testuser', 'testpassword', '30loops',
                                    auth_type='basic')

    # If the authentication succeeds, the is_authenticated flag must be set to
    # True
    assert auth.is_authenticated == True
    # Make sure the the request has been really made
    assert mock_request.called


@patch('httplib2.Http.request')
def test_an_invalid_authentication(mock_request):
    if env.has_key('auth'):
        del(env['auth'])
    response = Response({'status': 403})
    mock_request.return_value = (response, '')
    auth = Authenticate('testuser', 'testpassword', '30loops',
                                    auth_type='basic')
    assert auth.is_authenticated == False
    # Make sure the the request has been really made
    assert mock_request.called
