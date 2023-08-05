from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from socialtext.resources.pages import PageCommentManager

st = FakeServer()
page = st.pages.list("marketing")[0]

##########
# CREATE #
##########

def test_create():
    comment = "This is a *comment* using _wikitext_!"
    page.comment_set.create(comment)
    st.assert_called("POST", "/data/workspaces/marketing/pages/test_1/comments")

##########
# DELETE #
##########

@raises(NotImplementedError)
def test_delete():
    page.comment_set.delete()
    
########
# GET #
#######

@raises(NotImplementedError)
def test_get():
    page.comment_set.get()
    
########
# LIST #
########
@raises(NotImplementedError)
def test_list():
    page.comment_set.list()