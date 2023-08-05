from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext.resources.appliance_config import ApplianceConfiguration

st = FakeServer()

def test_get_config():
    config = st.appliance_config.get()
    st.assert_called('GET', '/data/config')
    assert_isinstance(config, ApplianceConfiguration)
    
    config.get()
    st.assert_called('GET', '/data/config')
    assert_isinstance(config, ApplianceConfiguration)