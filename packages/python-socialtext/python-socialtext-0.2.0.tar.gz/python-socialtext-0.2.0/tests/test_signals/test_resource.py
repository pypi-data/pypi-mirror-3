from unittest import TestCase
from nose.tools import assert_equal
from tests.utils import assert_isinstance

from socialtext.resources.signals import Signal

def test_get_mentioned_user_ids():
    # test signal mention
    body = "Hello {user: 123}!"
    signal = Signal(None, {"body": body})
    assert_equal(['123'], signal.get_mentioned_user_ids())

    # test multiple mentions
    body = "Hello {user: 123}, {user: 567}, and {user: 8910}!"
    signal.body = body
    expected = ['123', '567', '8910']
    assert_equal(expected, signal.get_mentioned_user_ids())


def test_is_user_mentioned():
    # User 123 is mentioned in this signal
    body = "Hello {user: 123}!"
    signal = Signal(None, {"body": body})
    assert_equal(True, signal.is_user_mentioned(123))

    # User 123 isn't mentioned in this signal
    signal.body = "Hello {user: 987}"
    assert_equal(False, signal.is_user_mentioned(123))