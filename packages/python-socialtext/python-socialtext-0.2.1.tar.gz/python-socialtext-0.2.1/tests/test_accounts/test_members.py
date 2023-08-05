from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.accounts import AccountMember, AccountMemberManager

st = FakeServer()
account = st.accounts.get(2)

##########
# CREATE #
##########

def test_create():
    data = {
        "username": "abc123"
    }

    member = account.member_set.create(data["username"])
    st.assert_called("POST", "/data/accounts/2/users", data=data)
