from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.users import User

st = FakeServer()

##########
# CREATE #
##########

@raises(NotImplementedError)
def test_create():
	st.users.create()

##########	
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
	st.users.delete(123)

#######
# GET #
#######

def assert_user_got(expected, **kwargs):
    u = st.users.get(123, **kwargs)
    st.assert_called('GET', '/data/users/123', params=expected)
    assert_isinstance(u, User)

def test_get_basic():
	user = st.users.get(123)
	st.assert_called('GET', '/data/users/123')

	user.get()
	st.assert_called('GET', '/data/users/123')

	user = st.users.get(user)
	st.assert_called('GET', '/data/users/123')
	
def test_get_with_minimal():
    minimal = True
    expected = {
        "minimal": 1
    }
    assert_user_got(expected, minimal=minimal)
    
    minimal = False
    expected = {}
    assert_user_got(expected, minimal=minimal)
	
def test_get_with_want_private_fields():
    want = True
    expected = {
        "want_private_fields": 1,
    }
    assert_user_got(expected, want_private_fields=want)
    
    want = False
    expected = {}
    assert_user_got(expected, want_private_fields=want)
    
def test_get_with_verbose():
    verbose = True
    expected = {
        "all": 1,
    }
    assert_user_got(expected, verbose=verbose)

    verbose = False
    expected = {}
    assert_user_got(expected, verbose=verbose)

########
# LIST #
########

def assert_users_listed(expected, **kwargs):
    data = st.users.list(**kwargs)
    st.assert_called('GET', '/data/users', params=expected)
    [assert_isinstance(u, User) for u in data]
    
def test_list_basic():
    assert_users_listed({})
    
def test_list_with_count():
    count = 10
    expected = {
        "count": count
    }
    assert_users_listed(expected, count=count)

def test_list_with_filter():
    filter = "bob"
    expected = {
        "filter": filter,
    }
    assert_users_listed(expected, filter=filter)
    
def test_list_with_offset():
    offset = 10
    expected = {
        "offset": offset
    }
    assert_users_listed(expected, offset=offset)
    
def test_list_with_order():
    order = st.users.ORDER_ALPHA
    expected = {
        "order": order,
    }
    assert_users_listed(expected, order=order)
    
@raises(ValueError)
def test_list_with_order_invalid():
    st.signals.list(order="foo")
    
def test_list_with_want_private_fields():
    want = True
    expected = {
        "want_private_fields": 1,
    }
    assert_users_listed(expected, want_private_fields=want)
    
    want = False
    expected = {}
    assert_users_listed(expected, want_private_fields=want)
    
