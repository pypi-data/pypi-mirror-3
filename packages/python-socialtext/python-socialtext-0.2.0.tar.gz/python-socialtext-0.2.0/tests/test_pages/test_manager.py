from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.pages import Page
from socialtext.resources.workspaces import Workspace

st = FakeServer()

##########
# CREATE #
##########

def assert_page_created(expected, **kwargs):
    body = "^^ Section 1\nThis is a test wiki page!"
        
    expected["content"] = body
    
    st.pages.create("Test 1", "marketing", body, **kwargs)
    
    st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')
    st.assert_called('PUT', '/data/workspaces/marketing/pages/Test%201', data=expected)
    
def test_create_basic():
    assert_page_created({})
    
def test_create_with_tags():
    tags = ["tag1", "tag2", "tag3"]
    expected = {
        "tags": tags,
    }
    assert_page_created(expected, tags=tags)
    
def test_create_with_edit_summary():
    edit_summary = "This is an edit summary!"
    expected = {
        "edit_summary": edit_summary,
    }
    assert_page_created(expected, edit_summary=edit_summary)
    
def test_create_with_signal_edit_summary():
    to_signal = True
    expected = {
        "signal_edit_summary": 1,
    }
    assert_page_created(expected, signal_edit_summary=to_signal)
    
    to_signal = False
    expected = {}
    assert_page_created(expected, signal_edit_summary=to_signal)
    
##########
# DELETE #
##########

def test_delete():
	page = st.pages.get('test_1', ws='marketing')

	page.delete()
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

	st.pages.delete('test_1', ws='marketing')
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

	st.pages.delete(page)
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

    
#######
# GET #
#######

def assert_page_got(page_name_or_id):
    st.assert_called('GET', '/data/workspaces/marketing/pages/' + page_name_or_id)

def test_get():
	page = st.pages.get('test_1', ws='marketing')
	assert_page_got('test_1')
	assert_isinstance(page, Page)

	page.get()
	assert_page_got('test_1')

	st.pages.get(page)
	assert_page_got('test_1')

def test_get_html():
	page = st.pages.get('test_1', ws='marketing')
	html = page.get_html()
	assert_page_got('test_1')
	assert_isinstance(html, str)
	assert '</div>' in html

def test_get_wikitext():
    page = st.pages.get('test_1', ws='marketing')
    wikitext = page.get_wikitext()
    assert_page_got('test_1')
    assert_isinstance(wikitext, str)
    assert '[Hello world]' in wikitext
    
########
# LIST #
########

def test_list_pages():
	pl = st.pages.list('marketing')
	st.assert_called('GET', '/data/workspaces/marketing/pages')
	[assert_isinstance(p, Page) for p in pl]
	
	# Get pages by workspace
	ws = st.workspaces.get('marketing')
	st.pages.list(ws)
	st.assert_called('GET', '/data/workspaces/marketing/pages')
	[assert_isinstance(p, Page) for p in pl]
	
##########
# UPDATE #
##########

def assert_page_updated(body, **kwargs):
    content = "New content!"
    expected = {
        "content": content,
    }
    st.pages.update("Test 1", content, ws="marketing")
    st.assert_called("PUT", "/data/workspaces/marketing/pages/Test%201")

def test_update_basic():
    assert_page_updated({})
    
def test_update_with_edit_summary():
    edit_summary = "This is an edit summary!"
    expected = {
        "edit_summary": edit_summary,
    }
    assert_page_updated(expected, edit_summary=edit_summary)

def test_update_with_signal_edit_summary():
    to_signal = True
    expected = {
        "signal_edit_summary": 1,
    }
    assert_page_updated(expected, signal_edit_summary=to_signal)

    to_signal = False
    expected = {}
    assert_page_updated(expected, signal_edit_summary=to_signal)
    
    