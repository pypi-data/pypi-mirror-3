from nose.tools import assert_equal, raises

from socialtext.resources.accounts import Account

from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance, assert_has_keys

st = FakeServer()

##########
# CREATE #
##########

def test_create():
    name = "Socialtext"
    data = {
        "name": name
    }
    st.accounts.create(name)
    st.assert_called('GET', '/data/accounts/2')
    st.assert_called('POST', '/data/accounts', data=data)
    
    
##########
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
    st.accounts.delete(2)
    
#######
# GET #
#######

def test_get():
    acct = st.accounts.get(2)
    st.assert_called('GET', '/data/accounts/2')
    assert_isinstance(acct, Account)
    
    acct.get()
    st.assert_called('GET', '/data/accounts/2')
    assert_isinstance(acct, Account)
    
    acct = st.accounts.get(acct)
    st.assert_called('GET', '/data/accounts/2')
    assert_isinstance(acct, Account)
    
########
# LIST #
########

def assert_accounts_listed(expected_query, **kwargs):
    data = st.accounts.list(**kwargs)
    st.assert_called('GET', '/data/accounts', params=expected_query)
    [assert_isinstance(a, Account) for a in data]
    
def test_list_basic():
    assert_accounts_listed({})
    
def test_list_expand():
    expand = True
    query = {
        "all": 1
    }
    assert_accounts_listed(query, expand=expand)
    
    expand = False
    query = {}
    assert_accounts_listed(query, expand=expand)
    
def test_list_filter():
    filter = "Soci"
    query = {
        "filter": filter
    }
    assert_accounts_listed(query, filter=filter)
    
    