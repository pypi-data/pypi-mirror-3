from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.signals import SignalLike, SignalLikeManager

st = FakeServer()
signal = st.signals.get(123)

def test_create():
	signal.like_set.create()
	st.assert_called("PUT", "/data/signals/123/likes/%s" % st.config.username)

	signal.like()
	st.assert_called("PUT", "/data/signals/123/likes/%s" % st.config.username)

def test_delete():
	signal.like_set.delete()
	st.assert_called("DELETE", "/data/signals/123/likes/%s" % st.config.username)

	signal.unlike()
	st.assert_called("DELETE", "/data/signals/123/likes/%s" % st.config.username)


def test_list():
	signal.like_set.list()

	st.assert_called("GET", "/data/signals/123/likes")

