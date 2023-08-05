from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.groups import Group, GroupManager, GroupTrashManager

st = FakeServer()

def test_delete():
	group = st.groups.get(21)
	workspace = st.workspaces.get("marketing")
	user = st.users.get(123)

	expected = [
		{ "user_id": 123},
		{ "workspace_id":  '123'}
	]

	group.trash([user, workspace])

	st.assert_called('POST', '/data/groups/21/trash', data=expected)