import mock

from nose.tools import assert_equal, assert_not_equal, assert_raises

from fakeserver import FakeServer

from socialtext.resources.base import BasicObject, Resource, get_id
from socialtext.resources.signals import Signal

cs = FakeServer()

def test_resource_repr():
    r = Resource(None, dict(foo='bar', baz='spam'))
    assert_equal(repr(r), "<Resource baz=spam, foo=bar>")
    
def test_get_id():
    assert_equal(get_id(4), '4')
    class O(object):
        id = 4
        def get_id(self):
            return self.id
    o = O()
    assert_equal(get_id(o), 4)
    
def test_eq():
    # two resources of different types: never equal
    r1 = Resource(None, {'id': 1})
    r2 = Signal(None, {'signal_id': 1})
    assert_not_equal(r1, r2)
    
    # Two resources with no ID: equal if their info is equal
    r1 = Resource(None, {'name': 'joe', 'age':12})
    r2 = Resource(None, {'name': 'joe', 'age':12})
    assert_equal(r1, r2)
