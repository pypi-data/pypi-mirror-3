from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance
from socialtext.resources.pages import PageTag, PageTagManager

st = FakeServer()
page = st.pages.list("marketing")[0]

##########
# CREATE #
##########

def test_create():
    t = page.tag_set.create("Test")
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/tags/Test")
    st.assert_called("PUT", "/data/workspaces/marketing/pages/test_1/tags/Test")
    assert_isinstance(t, PageTag)
    
##########
# DELETE #
##########

def test_delete():
    page.tag_set.delete("Test")
    st.assert_called("DELETE", "/data/workspaces/marketing/pages/test_1/tags/Test")
    
    t = page.tag_set.list()[0]
    t.delete()
    st.assert_called("DELETE", "/data/workspaces/marketing/pages/test_1/tags/Test")
    
    page.tag_set.delete(t)
    st.assert_called("DELETE", "/data/workspaces/marketing/pages/test_1/tags/Test")

#######
# GET #
#######

def test_get():
    t = page.tag_set.get("Test")
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/tags/Test")
    assert_isinstance(t, PageTag)
    
    t.get()
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/tags/Test")
    assert_isinstance(t, PageTag)
    
    t = page.tag_set.get(t)
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/tags/Test")
    assert_isinstance(t, PageTag)
    
########
# LIST #
########

def test_list():
    tags = page.tag_set.list()
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/tags")
    [assert_isinstance(t, PageTag) for t in tags]