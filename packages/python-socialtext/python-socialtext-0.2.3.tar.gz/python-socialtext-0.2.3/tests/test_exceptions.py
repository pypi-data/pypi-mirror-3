from socialtext.exceptions import (from_response, SocialtextException, BadRequest,
    Unauthorized, Forbidden, NotFound, Conflict, RequestEntityTooLarge,
    ServiceUnavailable)
from nose.tools import assert_equal, raises
from fakeserver import FakeServer

st = FakeServer()

@raises(BadRequest)
def test_400_bad_request():
	resp, body = st.client.get('/raise/400')
	raise from_response(resp, body)

@raises(Unauthorized)
def test_401_unauthorized():
	resp, body = st.client.get('/raise/401')
	raise from_response(resp, body)

@raises(Forbidden)
def test_403_forbidden():
	resp, body = st.client.get('/raise/403')
	raise from_response(resp, body)

@raises(NotFound)
def test_404_not_found():
	resp, body = st.client.get('/raise/404')
	raise from_response(resp, body)
	
@raises(Conflict)
def test_409_conflict():
	resp, body = st.client.get('/raise/409')
	raise from_response(resp, body)

@raises(RequestEntityTooLarge)
def test_413_request_entity_too_large():
	resp, body = st.client.get('/raise/413')
	raise from_response(resp, body)
	
@raises(ServiceUnavailable)
def test_503_service_unavailable():
    resp, body = st.client.get('/raise/503')
    raise from_response(resp, body)