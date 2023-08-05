import datetime

from nose.tools import assert_equal, raises

from tests.fakeserver import FakeServer
from tests.utils import assert_isinstance, assert_has_keys

from socialtext.resources.signals import Signal


st = FakeServer()

##########
# CREATE #
##########

def assert_signal_created(expected_body, **kwargs):
    expected_body["signal"] = "Hello world!"
    st.signals.create("Hello world!", **kwargs)
    st.assert_called('GET', '/data/signals/123')
    st.assert_called('POST', '/data/signals', data=expected_body)

def test_create_basic():
    assert_signal_created({})

def test_create_with_accounts():
    accounts = [1,2,3]
    expected = {
        "account_ids": [str(a) for a in accounts]
    }
    assert_signal_created(expected, accounts=accounts)
    
def test_create_with_all_accounts():
    all_accounts = True
    expected = {
        "all_accounts": 1
    }
    assert_signal_created(expected, all_accounts=all_accounts)
    
    # test that accounts are ignored when all_accounts=True
    accounts = [1,2,3]
    expected = {
        "all_accounts": 1
    }
    assert_signal_created(expected, all_accounts=all_accounts)
    
def test_create_with_annotations():
    annotations = [
        {
            "type1": {
                "foo": "bar"
            }
        },
        {
            "type2": {
                "hello": "world"
            }
        }
    ]
    expected = {
        "annotations": annotations
    }
    assert_signal_created(expected, annotations=annotations)
    
@raises(ValueError)
def test_create_with_annotations_invalid():
    annotations = [
        {
            "type1": { "foo": "bar" },
            "type2": { "foo": "bar" },
        }
    ]
    st.signals.create("Hello world!", annotations=annotations)

def test_create_with_at_datetime():
    now = datetime.datetime.now()
    expected = {
        "at": now.isoformat()
    }
    assert_signal_created(expected, at=now)

def test_create_with_at_string():
    now = datetime.datetime.now().isoformat()
    expected = {
        "at": now
    }
    assert_signal_created(expected, at=now)

def test_create_with_at_unicode():
    now = u'unicode string'
    expected = {
        "at": now
    }
    assert_signal_created(expected, at=now)

@raises(ValueError)
def test_create_with_at_invalid():
    at = 123
    st.signals.create("Hello world!", at=at)
    
def test_create_with_attachments():
    attachments = ["hash1", "hash2", "hash3"]
    expected = {
        "attachments": attachments,
    }
    assert_signal_created(expected, attachments=attachments)
    
def test_create_with_groups():
    groups = [1,2,3]
    expected = {
        "group_ids": [str(g) for g in groups],
    }
    assert_signal_created(expected, groups=groups)
    
def test_create_with_inreplyto_signal_instance():
    in_reply_to = st.signals.get(123)
    expected = {
        "in_reply_to" : {
            "signal_id": in_reply_to.signal_id,
        }
    }
    assert_signal_created(expected, in_reply_to=in_reply_to)
    
def test_create_with_inreplyto_signal_int():
    in_reply_to = 123
    expected = {
        "in_reply_to": {
            "signal_id": str(in_reply_to)
        }
    }
    assert_signal_created(expected, in_reply_to=in_reply_to)
    
def test_create_with_inreplyto_search():
    in_reply_to = "annotations:foo|bar|yay"
    expected = {
        "in_reply_to": {
            "search": in_reply_to
        }
    }
    assert_signal_created(expected, in_reply_to=in_reply_to)
    
def test_create_with_recipient_user():
    recipient = st.users.list()[0]
    expected = {
        "recipient": {
            "id": recipient.get_id()
        }
    }
    assert_signal_created(expected, recipient=recipient)
    
def test_create_with_recipient_user_id():
    recipient = 123
    expected = {
        "recipient": {
            "id": str(recipient),   
        }
    }
    assert_signal_created(expected, recipient=recipient)
    
@raises(ValueError)
def test_create_with_recipient_invalid():
    # usernames are invalid
    recipient = "joe@example.com"
    st.signals.create("Hello world", recipient=recipient)

##########
# DELETE #
##########

def test_delete_signals():
    signal = st.signals.get(123)

    signal.delete()
    st.assert_called('DELETE', '/data/signals/123')

    st.signals.delete(123)
    st.assert_called('DELETE', '/data/signals/123')

    st.signals.delete(signal)
    st.assert_called('DELETE', '/data/signals/123')


#######
# GET #
#######

def test_get():
    sig = st.signals.get(123)
    assert_isinstance(sig, Signal)

    sig.get()
    assert_isinstance(sig, Signal)

    sig = st.signals.get(sig)
    assert_isinstance(sig, Signal)

########
# HIDE #
########

def test_hide():
    sig = st.signals.get(123)

    sig.hide()
    st.assert_called('PUT', '/data/signals/123/hidden')

    st.signals.hide(123)
    st.assert_called('PUT', '/data/signals/123/hidden')

    st.signals.hide(sig)
    st.assert_called('PUT', '/data/signals/123/hidden')

########
# LIST #
########

def assert_signals_listed(expected_query, **kwargs):
    data = st.signals.list(**kwargs)
    st.assert_called('GET', '/data/signals', params=expected_query)
    [assert_isinstance(s, Signal) for s in data]

def test_list_basic():
    assert_signals_listed({})

def test_list_with_accounts():
    accounts = [1,2,3]
    expected = {
        # the accounts will be strings
        # because the manager calls get_id on them.
        "accounts": [str(a) for a in accounts],
    }
    assert_signals_listed(expected, accounts=accounts)

def test_list_with_after_datetime():
    now = datetime.datetime.now()
    expected = {
        "after": now.isoformat()
    }
    assert_signals_listed(expected, after=now)
    
def test_list_with_after_string():
    now = "There-Is-No-Format-Check"
    expected = {
        "after": now
    }
    assert_signals_listed(expected, after=now)
    
def test_list_with_after_signal():
    signal = st.signals.list()[0]
    expected = {
        "after": signal.at
    }
    assert_signals_listed(expected, after=signal)

@raises(ValueError)
def test_list_with_after_invalid():
    after = 123
    st.signals.list(after=after)

def test_list_with_before_datetime():
    now = datetime.datetime.now()
    expected = {
        "before": now.isoformat()
    }
    assert_signals_listed(expected, before=now)
    
def test_list_with_before_string():
    now = "There-Is-No-Format-Check"
    expected = {
        "before": now
    }
    assert_signals_listed(expected, before=now)

def test_list_with_before_signal():
    signal = st.signals.list()[0]
    expected = {
        "before": signal.at
    }
    assert_signals_listed(expected, before=signal)

@raises(ValueError)
def test_list_with_before_invalid():
    before = 123
    st.signals.list(before=before)

def test_list_with_direct():
    direct = st.signals.DIRECT_BOTH
    expected = {
        "direct": direct
    }
    assert_signals_listed(expected, direct=direct)

@raises(ValueError)
def test_list_with_direct_invalid():
    direct = "foo"
    st.signals.list(direct=direct)

def test_list_with_direction():
    direction = st.signals.DIRECTION_ASC
    expected = {
        "direction": direction
    }
    assert_signals_listed(expected, direction=direction)

@raises(ValueError)
def test_list_with_direction_invalid():
    direction = "foo"
    st.signals.list(direction=direction)

def test_list_with_following():
    # test for True
    following = True
    expected = {
        "following": 1
    }
    assert_signals_listed(expected, following=following)

    # test for false
    following = False
    expected = {} # it will be an empty query
    assert_signals_listed(expected, following=following)

def test_list_with_groups():
    groups = [1,2,3]
    expected = {
        # the groups will be strings
        # because the manager calls get_id on them.
        "groups": [str(g) for g in groups],
    }
    assert_signals_listed(expected, groups=groups)

def test_list_with_hidden():
    hidden = True
    expected = {
        "hidden": 1
    }
    assert_signals_listed(expected, hidden=hidden)

    # test when hidden is False
    hidden = False
    expected = {}
    assert_signals_listed(expected, hidden=hidden)

def test_list_with_limit():
    limit = 50
    expected = {
        "limit": limit
    }
    assert_signals_listed(expected, limit=limit)

def test_list_with_offset():
    offset = 50
    expected = {
        "offset": offset
    }
    assert_signals_listed(expected, offset=offset)

def test_list_with_order():
    order = st.signals.ORDER_DATE
    expected = {
        "order": order
    }
    assert_signals_listed(expected, order=order)

@raises(ValueError)
def test_list_with_order_invalid():
    order = "foo"
    st.signals.list(order=order)
    
def test_list_with_q():
    q = "creator:3551"
    expected = {
        "q": q,
    }
    assert_signals_listed(expected, q=q)

def test_list_with_sender_user():
    sender = st.users.list()[0]
    expected = {
        "sender": sender.get_id()
    }
    assert_signals_listed(expected, sender=sender)

def test_list_with_sender_username():
    sender = "abc123"
    expected = {
        "sender": sender
    }
    assert_signals_listed(expected, sender=sender)
