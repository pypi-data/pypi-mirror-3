from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance
from socialtext.resources.pages import Page, PageBacklinkManager

st = FakeServer()
page = st.pages.list("marketing")[0]

##########
# CREATE #
##########

@raises(NotImplementedError)
def test_create():
    page.backlink_set.create()
    

##########
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
    page.backlink_set.delete()
    
########
# GET #
#######

@raises(NotImplementedError)
def test_get():
    page.backlink_set.get()
    
########
# LIST #
########

def test_list():
    bl = page.backlink_set.list()
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_1/backlinks")
    [assert_isinstance(b, Page) for b in bl]
