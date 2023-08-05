from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.users import User

st = FakeServer()

def test_is_member_of_account():
	accounts = [{ "account_id": "123"}, {"account_id": "987"}]
	user = st.users.load({"accounts": accounts})
	assert_equal(True, user.is_member_of_account("123"))
	assert_equal(True, user.is_member_of_account("987"))
	assert_equal(False, user.is_member_of_account("1000"))

def test_is_member_of_group():
	groups = [{ "group_id": "123"}, {"group_id": "987"}]
	user = st.users.load({"groups": groups})
	assert_equal(True, user.is_member_of_group("123"))
	assert_equal(True, user.is_member_of_group("987"))
	assert_equal(False, user.is_member_of_group("1000"))