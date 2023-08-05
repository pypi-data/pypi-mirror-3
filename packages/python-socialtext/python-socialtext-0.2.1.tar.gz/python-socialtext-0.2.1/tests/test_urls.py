from nose.tools import assert_equal, raises
from socialtext.urls import make_data_url

@raises(ValueError)
def test_invalid_url_key():
	invalid_key = "foo"
	make_data_url(invalid_key)

def test_simple_url():
	# no parameters
	key = "workspaces"
	expected = "/data/workspaces"
	assert_equal(expected, make_data_url(key))

def test_complex_url():
	key = "pageattachment"
	format = {
		"ws_name" : "test_ws",
		"page_name" : "test_page",
		"attachment_id": "123",
	}
	expected = "/data/workspaces/test_ws/pages/test_page/attachments/123"
	assert_equal(expected, make_data_url(key, **format))
