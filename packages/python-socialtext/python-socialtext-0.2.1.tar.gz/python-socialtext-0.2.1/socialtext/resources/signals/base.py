import re
import datetime

from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

from socialtext.resources.signals.likes import SignalLikeManager

class Signal(Resource):

    def __init__(self, *args, **kwargs):
        super(Signal, self).__init__(*args, **kwargs)
        self.like_set = SignalLikeManager(self.manager.api, self)

    def __repr__(self):
        return "<Signal: %s>" % self.signal_id

    def delete(self):
        """
        Delete this signal.
        
        .. warning::
            This will permanently delete the Signal from the database. Only Business Administrators
            can delete signals.
        """
        return self.manager.delete(self)
    
    def get_id(self):
        """
        Get the ID that represents this signal. The signal_id attribute is required.
        
        :rtype: string
        """
        assert hasattr(self, 'signal_id'), "The signal does not have a 'signal_id' attribute."
        return self.signal_id
    
    def get_mentioned_user_ids(self):
        """
        Get a list of User IDs that are mentioned in the Signal.
        
        :rtype: list of string User IDs
        """
        regex = re.compile(r'{user: (\d+)}')
        user_ids = []
        for m in regex.finditer(self.body):
            user_ids.append(m.groups(1)[0])
        return user_ids

    def hide(self):
        """
        Hide this Signal from retrieving or searching. It will still
        be accessible through explicit requests by the Signal creator
        and Business Administrators

        .. warning::
            A signal can not be made "unhidden". Please use with caution.
        """
        self.manager.hide(self)
    
    def is_user_mentioned(self, user_id):
        """
        Determines if a user with the provided user_id is mentioned
        in this signal's body.
        
        :rtype: boolean if the user_id is mentioned
        """
        if self.body.find("{user: %s}" % user_id) >= 0:
            return True
        return False

    def like(self):
        """
        Likes this Signal.
        """
        self.like_set.create()

    def unlike(self):
        """
        Unlike this Signal.
        """
        self.like_set.delete()
    
    @property    
    def at_datetime(self):
        return datetime.datetime.fromtimestamp(self.at)
        
class SignalManager(Manager):
    """
    Manage :class:`Signal` resources.
    """
    ORDER_RELEVANCE = "relevance"
    ORDER_DATE = "date"
    ORDER_SENDER = "sender"
    ORDER_CHOICES = [
        ORDER_RELEVANCE,
        ORDER_DATE,
        ORDER_SENDER
    ]
    
    DIRECTION_ASC = "asc"
    DIRECTION_DESC = "desc"
    DIRECTION_CHOICES = [
        DIRECTION_ASC,
        DIRECTION_DESC
    ]
    
    DIRECT_BOTH = "both"
    DIRECT_SENT = "sent"
    DIRECT_RECEIVED = "received"
    DIRECT_CHOICES = [
        DIRECT_BOTH,
        DIRECT_SENT,
        DIRECT_RECEIVED
    ]
    
    resource_class = Signal
    
    def list(self, accounts=[], after=None, before=None, direct=None, direction=None, following=False,
        groups=[], hidden=False, limit=None, offset=None, order=None, q=None, sender=None):
        """
        Get a list of all signals.
        
        :param accounts: Filter the list to include only signals visible to the list of :class:`Account` (or IDs of Accounts).
        :param after: Filter the list to include only signals after a certain date. Callers can pass a datetime object,
                      :class:`Signal` object, or an ISO string representation.
        :param before: Filter the list to include only signals before a certain date. Callers can pass a datetime object,
                       :class:`Signal` object, or an ISO string representation.
        :param direct: Expand the results list to include direct messages. The default is that no direct
                       messages are included in the results. Must be one of DIRECT_CHOICES.
        :param direction: Determines the direction of the sort (ascending or descending). Must be one of hte `DIRECTION_CHOICES`.
        :param following: If True, the list will only include Signals from people the calling user is following.
        :param groups: Filter the list to include only signals visible to the list of :class:`Group` (or IDs of Groups).
        :param hidden: Filter the list to include only signals that have been 'hidden' but not yet deleted.
        :param limit: The maximum number of results to return.
        :param offset: Returns results starting at this offset from the beginning of the list.
        :param order: determines the sort order of the results. Must be one of the `ORDER_CHOICES`
        :param q: A query to filter on fields indexed for searching.
        :param sender: Filter the list to include only signals sent by the :class:`User` (or ID/username of the User).
        :rtype: list of :class:`Signal`
        """
        
        query = {}
        
        if accounts:
            acct_ids = [get_id(acct) for acct in accounts]
            query['accounts'] = acct_ids
            
        if after:
            if isinstance(after, datetime.datetime):
                query['after'] = after.isoformat()
            elif isinstance(after, Signal):
                query['after'] = after.at
            elif isinstance(after, str):
                query['after'] = after
            else:
                raise ValueError("The after kwarg must be a datetime object, String object, or ISO string.")

        if before:
            if isinstance(before, datetime.datetime):
                query['before'] = before.isoformat()
            elif isinstance(before, Signal):
                query['before'] = before.at
            elif isinstance(before, str):
                query['before'] = before
            else:
                raise ValueError("The before kwarg must be a datetime object, String object, or ISO string.")
            
        if direct:
            if not direct in self.DIRECT_CHOICES:
                raise ValueError("The provided direct value is invalid. It must be one of SignalManager.DIRECT_CHOICS")
            query['direct'] = direct
        
        if direction:
            if not direction in self.DIRECTION_CHOICES:
                raise ValueError("The provided direction value is invalid. It must be one of SignalManager.DIRECTION_CHOICES")
            query['direction'] = direction
            
        if following:
            query['following'] = 1
            
        if groups:
            group_ids = [get_id(group) for group in groups]
            query['groups'] = group_ids
            
        if hidden:
            query['hidden'] = 1
            
        if limit:
            query['limit'] = int(limit)
            
        if offset:
            query['offset'] = int(offset)
        
        if order:
            if not order in self.ORDER_CHOICES:
                raise ValueError("The provided order value is invalid. It must be one of SignalManager.ORDER_CHOICES")
            query['order'] = order
            
        if q:
            query["q"] = q
            
        if sender:
            query['sender'] = get_id(sender)
        
        url = make_data_url("signals")
        
        return self._list(url, params=query)
    
    def get(self, signal):
        """
        Get a specific signal.
        
        :param signal: The :class:`Signal` (or ID of the Signal) to get
        :rtype: :class:`Signal`
        """
        url = make_data_url("signal", signal_id=get_id(signal))
        return self._get(url)
    
    def create(self, body, accounts=[], all_accounts=False, annotations=[], at=None, attachments=[], groups=[], in_reply_to=None, recipient=None):
        """
        Create a signal in Socialtext.
        
        :param body: The body of the signal.
        :param accounts: A list of :class:`Account` (or Account ID) that the signal should be posted to.
        :param all_accounts: If True, the signal will be sent to all of the user's accounts. Any values in
                             the `accounts` keyword argument will be ignored.
        :param annotations: A list of meta-data to apply to the signal. Each list item must be a dictionary
                            with a single key to specify the annotation type and the value of that key must
                            be a dictionary to store the key/value data.
        :param at: A datetime object or ISO datetime string that will be used to set the time of the signal
                   This parameter is helpful when migrating content from another microblogging system.
                   Only Business Administrators can create signals using this parameter.
        :param in_reply_to: The :class:`Signal` (or ID of the signal) to reply to. If a string is
                            provided, it will be considered a search string. The posted signal will
                            be in reply to the first result of the search.
        :param groups: A list of :class:`Group` (or Group ID) to post the signal to.
        :param attachments: A list of Upload hash-IDs that represent the files to attach to the Signal.
                            Use the :class:`UploadManager` to generate the hash-IDs.
                            The total size of all attachments can not exceed 50MB.
        :param recipient: A :class:`User` (or User ID or username) to send a private message to.
                          If a recipient is specified, the accounts and groups parameters will be ignored.
        
        :rtype: :class:`Signal`
        """
        signal = {"signal" : body}
        
        if all_accounts:
            signal['all_accounts'] = 1
        elif accounts:
            signal['account_ids'] = [get_id(a) for a in accounts]
            
        if annotations:
            # validate the annotations format
            for ann in annotations:
                # each annotation dictionary should only have one outer key to specify type.
                if len(ann.keys()) != 1:
                    raise ValueError("The list of provided annotations is malformed. The outer dictionary can only have one key.")
                
                # the annotation type is the value of the first (and only) key.
                annotation_type = ann.keys()[0]
                
                # the attribute key/value pairs is the first (and only) value.
                attributes_dict = ann.values()[0]
                
                # make sure the attribute key/value pairs is a dict
                if not isinstance(attributes_dict, dict):
                    raise ValueError("The annotation of type %s must contain a dictionary of attribute key/value pairs." % annotation_type)
                    
            # the annotations passed our basic checks
            signal['annotations'] = annotations
        
        if in_reply_to:
            if isinstance(in_reply_to, str):
                # we have a search string
                signal["in_reply_to"] = {"search": in_reply_to}
            else:
                # reply to the provided Signal instance or make
                # the value into an ID.
                signal["in_reply_to"] = {"signal_id" : get_id(in_reply_to)}
        
        if groups:
            signal["group_ids"] = [get_id(g) for g in groups]
            
        if recipient:
            recipient_id = get_id(recipient)
            
            # This check is in place because the API documentation
            # is unclear as to whether or not we could specify
            # a username as a recipient. Example:
            # { "username": "joe@example.com" }
            if not isinstance(recipient_id, int) and not recipient_id.isdigit():
                raise ValueError("The provided recipient's ID is invalid. It must be a number.")
            signal["recipient"] = { "id": recipient_id }

        if at:
            if isinstance(at, datetime.datetime):
                signal["at"] = at.isoformat()
            elif isinstance(at, str) or isinstance(at, unicode):
                signal["at"] = at
            else:
                raise ValueError("The 'at' parameter must be a datetime object or ISO string representation of a date.")
        
        if attachments:
            signal['attachments'] = attachments
        
        url = make_data_url("signals")
        resp, body = self.api.client.post(url, data=signal)
        signal_id = resp.headers.get('x-signal-id', None)
        return self.get(signal_id)
    
    def delete(self, signal):
        """
        Delete a signal.
        
        .. warning::
            This will permanently delete the Signal from the database. Only Business Administrators
            can delete signals.
        
        :param signal: The :class:`Signal` (or ID of the Signal) to delete
        """
        url = make_data_url("signal", signal_id=get_id(signal))
        self._delete(url)

    def hide(self, signal):
        """
        Hide a signal from retrieval and searching. The signal will still be
        accessible through explicit requests by the signal creator and
        business administrators.

        .. warning::
            A signal can not be made "unhidden". Please use with caution.

        :param signal: The :class:`Signal` (or Signal ID or Signal Hash) to hide.
        """
        url = make_data_url("signal_hide", signal_id=get_id(signal))
        self._update(url, {})

