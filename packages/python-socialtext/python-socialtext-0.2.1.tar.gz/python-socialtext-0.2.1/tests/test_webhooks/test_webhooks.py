from nose.tools import assert_equal, raises
from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance

from socialtext.resources.webhooks import Webhook

st = FakeServer()

def test_list_webhooks():
	wl = st.webhooks.list()
	st.assert_called('GET', '/data/webhooks')
	[assert_isinstance(w, Webhook) for w in wl]

def test_get_webhooks():
	hook = st.webhooks.get(123)
	st.assert_called('GET', '/data/webhooks/123')
	assert_isinstance(hook, Webhook)
	assert_equal(hook.id, 123)
	assert_equal(hook.creator_id, 110)

	hook = hook.get()
	st.assert_called('GET', '/data/webhooks/123')

def test_delete_webhooks():
	hook = st.webhooks.get(123)
	hook.delete()
	st.assert_called('DELETE', '/data/webhooks/123')

	st.webhooks.delete(hook)
	st.assert_called('DELETE', '/data/webhooks/123')

	st.webhooks.delete(123)
	st.assert_called('DELETE', '/data/webhooks/123')

def test_create_webhook():
	action = "signal.create"
	url = "https://example.com"
	account_id = 1
	details = { 'to_user' : 123 }
	hook = st.webhooks.create(action, url, account_id=account_id, details=details)

	# Socialtext does not return a JSON of the new webhook
	# instead, it returns a Location header.
	# The API should parse the ID from the header and then
	# load a :class:`Webhook` from the POST dict
	st.assert_called('POST', '/data/webhooks')

	assert_isinstance(hook, Webhook)
	
def test_create_page_webhook():
	action = "page.create"
	url = "https://example.com"
	workspace_id = 123
	page_id = 'example_page'
	hook = st.webhooks.create_page_webhook(action, url,
		workspace_id=workspace_id, page_id=page_id)
	
	assert_isinstance(hook, Webhook)
	assert_equal(getattr(hook, 'class'), action)
	assert_equal(hook.url, url)
	assert_equal(hook.workspace_id, workspace_id)
	assert_equal(hook.details.page_id, page_id)

@raises(ValueError)
def test_create_page_webhook_invalid_action():
	action = "page.foo"
	url = "https://example.com"
	st.webhooks.create_page_webhook(action, url)

def test_create_signal_webhook():
	action = "signal.create"
	url = "https://example.com"
	account_id = 1
	user_id = 123
	tag = "abc123"
	hook = st.webhooks.create_signal_webhook(action, url, 
		account_id=account_id, user_id=user_id, tag=tag)

	assert_isinstance(hook, Webhook)
	assert_equal(getattr(hook, 'class'), action)
	assert_equal(hook.url, url)
	assert_equal(hook.account_id, account_id)
	assert_equal(hook.details.to_user, user_id)
	assert_equal(hook.details.tag, tag)

@raises(ValueError)
def test_create_signal_webhook_invalid_action():
	action = "signal.foo"
	url = "https://example.com"
	st.webhooks.create_signal_webhook(action, url)