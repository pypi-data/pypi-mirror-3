from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance
from socialtext.resources.pages import Page, PageFrontlinkManager

st = FakeServer()
page = st.pages.list("marketing")[1]

##########
# CREATE #
##########

@raises(NotImplementedError)
def test_create():
    page.frontlink_set.create()
    

##########
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
    page.frontlink_set.delete()
    
########
# GET #
#######

@raises(NotImplementedError)
def test_get():
    page.frontlink_set.get()
    
########
# LIST #
########

def test_list():
    bl = page.frontlink_set.list()
    st.assert_called("GET", "/data/workspaces/marketing/pages/test_2/frontlinks")
    [assert_isinstance(b, Page) for b in bl]
