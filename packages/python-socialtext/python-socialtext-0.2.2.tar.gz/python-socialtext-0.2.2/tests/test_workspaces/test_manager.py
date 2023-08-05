from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.workspaces import Workspace

st = FakeServer()

##########
# CREATE #
##########

def assert_ws_created(expected, **kwargs):
    name = "marketing"
    title = "Marketing"
    account = 2
    st.workspaces.create(name, title, account, **kwargs)
    
    expected["name"] = name
    expected["title"] = title
    expected["account_id"] = str(account)
    
    st.assert_called('GET', '/data/workspaces/marketing')
    st.assert_called('POST', '/data/workspaces', data=expected)

def test_create_basic():
	assert_ws_created({})
	
def test_create_with_cascade_css():
    cascade = True
    expected = {
        "cascade_css": 1
    }
    assert_ws_created(expected, cascade_css=cascade)
    
    cascade = False
    expected = {}
    assert_ws_created(expected, cascade_css=cascade)
    
def test_create_with_cloned_pages():
    # clone with Workspace instance
    clone = st.workspaces.list()[0]
    expected = {
        "clone_pages_from": clone.name
    }
    assert_ws_created(expected, clone_pages_from=clone)
    
    # clone from name string
    clone = "marketing"
    expected = {
        "clone_pages_from": clone
    }
    assert_ws_created(expected, clone_pages_from=clone)
    
def test_create_with_customjs():
    uri = "http://path/to/js"
    name = "custom.js"
    expected = {
        "customjs_uri": uri,
        "customjs_name": name
    }
    assert_ws_created(expected, customjs_name=name, customjs_uri=uri)
    
@raises(ValueError)
def test_create_with_customjs_no_uri():
    st.workspaces.create("name", "title", 1, customjs_name="jsname")

@raises(ValueError)
def test_create_with_customjs_no_name():
    st.workspaces.create("name", "title", 1, customjs_uri="jsuri")
    
def test_create_with_groups():
    groups = [1,2,3]
    expected = {
        "groups": [{"group_id": str(g)} for g in groups]
    }
    assert_ws_created(expected, groups=groups)
    
def test_create_with_permissions():
    perm = st.workspaces.PERM_PRIVATE
    expected = {
        "permission_set": perm
    }
    assert_ws_created(expected, permission_set=perm)
    
@raises(ValueError)
def test_create_with_permissions_invalid():
    perm = "Foo!"
    st.workspaces.create("name", "title", 1, permission_set=perm)
    
def test_create_with_show_title_below_logo():
    show = True
    expected = {
        "show_title_below_logo": 1,
    }
    assert_ws_created(expected, show_title_below_logo=show)
    
    show = False
    expected = {}
    assert_ws_created(expected, show_title_below_logo=show)
    
def test_create_with_show_welcome_message_below_logo():
    show = True
    expected = {
        "show_welcome_message_below_logo": 1,
    }
    assert_ws_created(expected, show_welcome_message_below_logo=show)
    
    show = False
    expected = {}
    assert_ws_created(expected, show_welcome_message_below_logo=show)
    
def test_create_with_skin_name():
    skin = "super-skin"
    expected = {
        "skin_name": skin
    }
    assert_ws_created(expected, skin_name=skin)

##########
# DELETE #
##########

def test_delete():
	ws = st.workspaces.get(123)
	ws.delete()
	st.assert_called('DELETE', '/data/workspaces/marketing')

	st.workspaces.delete(ws)
	st.assert_called('DELETE', '/data/workspaces/marketing')

	st.workspaces.delete(123)
	st.assert_called('DELETE', '/data/workspaces/123')

#######
# GET #
#######

def test_get():
	ws = st.workspaces.get(123)
	st.assert_called('GET', '/data/workspaces/123')

	ws = st.workspaces.get('marketing')
	st.assert_called('GET', '/data/workspaces/marketing')

	assert_isinstance(ws, Workspace)
	assert_equal(123, ws.id)
	assert_equal('marketing', ws.name)

	ws.get()
	st.assert_called('GET', '/data/workspaces/marketing')
	
########
# LIST #
########

def test_list():
	wl = st.workspaces.list()
	st.assert_called('GET', '/data/workspaces')
	[assert_isinstance(w, Workspace) for w in wl]