from nose.tools import assert_equal, raises

from socialtext.resources.groups import Group

from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance, assert_has_keys

st = FakeServer()

##########
# CREATE #
##########

def assert_group_created(data, **kw):
    data["name"] = "Mac fans"
    g = st.groups.create("Mac fans", **kw)
    st.assert_called("GET", "/data/groups/21")
    st.assert_called("POST", "/data/groups", data=data)
    assert_isinstance(g, Group)
    
def test_create_basic():
    assert_group_created({})
    
def test_create_account():
    acct = st.accounts.list()[0]
    data = {
        "account_id": acct.get_id()
    }
    assert_group_created(data, account=acct)
    
    acct = 123
    data = {
        "account_id": str(acct)
    }
    assert_group_created(data, account=acct)
    
def test_create_description():
    desc = "This is an awesome group!"
    data = {
        "description": desc
    }
    assert_group_created(data, description=desc)
    
def test_create_permission_set():
    perm = st.groups.PERMISSION_CHOICES[0]
    data = {
        "permission_set": perm
    }
    assert_group_created(data, permission_set=perm)
    
@raises(ValueError)
def test_create_permission_set_invalid():
    st.groups.create("fooname", permission_set="foo")
    
##########
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
    st.groups.delete(123)

#######
# GET #
#######

def assert_group_get(query, **kw):
    g = st.groups.get(21, **kw)
    st.assert_called('GET', '/data/groups/21', params=query)
    assert_isinstance(g, Group)

def test_get_basic():
    group = st.groups.get(21)
    st.assert_called('GET', '/data/groups/21')
    assert_isinstance(group, Group)
    
    group.get()
    st.assert_called('GET', '/data/groups/21')
    assert_isinstance(group, Group)
    
    group = st.groups.get(group)
    st.assert_called('GET', '/data/groups/21')
    assert_isinstance(group, Group)
    
def test_get_show_members():
    show = True
    query = {
        "show_members": 1
    }
    assert_group_get(query, show_members=show)
    
    show = False
    query = {}
    assert_group_get(query, show_members=show)
    
def test_get_can_update_perms():
    can = True
    query = {
        "can_update_perms": 1
    }
    assert_group_get(query, can_update_perms=can)
    
    can = False
    query = {}
    assert_group_get(query, can_update_perms=can)
    
    
    
########
# LIST #
########

def assert_groups_listed(query, **kw):
    data = st.groups.list(**kw)
    st.assert_called('GET', '/data/groups', params=query)
    [assert_isinstance(g, Group) for g in data]
    
def test_list_basic():
    assert_groups_listed({})
    
def test_list_expand():
    expand = True
    query = {
        "all": 1
    }
    assert_groups_listed(query, expand=expand)
    
    expand = False
    query = {}
    assert_groups_listed(query, expand=expand)
    
def test_list_filter():
    filter = "description:foo"
    query = {
        "filter": filter
    }
    assert_groups_listed(query, filter=filter)
    
def test_list_discoverable():
    discoverable = st.groups.DISCOVERABLE_PUBLIC
    query = {
        "discoverable": discoverable
    }
    assert_groups_listed(query, discoverable=discoverable)
    
@raises(ValueError)
def test_list_disocverable_invalid():
    discoverable = "foo"
    st.groups.list(discoverable=discoverable)
    
def test_list_show_members():
    show = True
    query = {
        "show_members": 1
    }
    assert_groups_listed(query, show_members=show)
    
    show = False
    query = {}
    assert_groups_listed(query, show_members=show)
