from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url


class Webhook(Resource):
    def __repr__(self):
        return "<Webhook: %s>" % self.id

    def delete(self):
        """
        Delete this webhook.
        """
        self.manager.delete(self)

    def get_id(self):
        """
        Get the ID of this webhook. The id attribute is required.

        :rtype: string
        """
        assert hasattr(self, 'id'), "The webhook does not have an 'id' attribute."
        return self.id


class WebhookManager(Manager):
    """
    Manage :class:`Webhook` resources.
    """
    resource_class = Webhook
    ACTION_PAGE_CREATE = "page.create"
    ACTION_PAGE_DELETE = "page.delete"
    ACTION_PAGE_TAG = "page.tag"
    ACTCION_PAGE_UPDATE = "page.update"
    ACTION_PAGE_WATCH = "page.watch"
    ACTION_PAGE_UNWATCH = "page.unwatch"
    ACTION_PAGE_ALL = "page.*"
    ACTION_PAGES = [
        ACTION_PAGE_CREATE,
        ACTION_PAGE_DELETE,
        ACTION_PAGE_TAG,
        ACTCION_PAGE_UPDATE,
        ACTION_PAGE_WATCH,
        ACTION_PAGE_UNWATCH,
        ACTION_PAGE_ALL,
    ]

    ACTION_SIGNAL_CREATE = "signal.create"
    ACTION_SIGNALS = [
        ACTION_SIGNAL_CREATE
    ]
    
    def list(self):
        """
        Get a list of all webhooks the current user has access to.
        
        :rtype: list of :class:`Webhook`.
        """
        return self._list(make_data_url("webhooks"))
        
    def get(self, webhook):
        """
        Get a single webhook.

        .. note::
            Only Business Administrators can get webhook details.
        
        :param webhook: The :class:`Webhook` (or ID of the webhook) to get
        :rtype: :class:`Webhook`.
        """
        url = make_data_url("webhook", webhook_id=get_id(webhook))
        return self._get(url)
        
    def create(self, webhook_class, callback_url, account_id=None, group_id=None,
        workspace_id=None, details=None):
        """
        Create a webhook in Socialtext.

        .. note::
            This is a general method. Try using a more specific method
            like :func:`create_signal_webhook` or :func:`create_page_webhook`
        
        :param webhook_class: A string representation of the webhook class. Ex: "signal.create"
        :param callback_url: The URl the webhook will POST to.
        :param account_id: The ST account ID this webhook will watch for actions in.
        :param group_id: The ST group ID this webhook will watch for actions in.
        :param workspace_id: The ST workspace name this webhook will watch for actions in.
        :param details: Webhook class sepcific details to give the webhook.

        :rtype: :class:`Webhook`
        """
        webhook = {"class" : webhook_class, "url" : callback_url}
        if account_id:
            webhook['account_id'] = int(account_id)
        if group_id:
            webhook['group_id'] = int(group_id)
        if workspace_id:
            webhook['workspace_id'] = int(workspace_id)
        if details:
            webhook['details'] = details
        url = make_data_url("webhooks")
        
        resp, content = self.api.client.post(url, data=webhook)
        location = resp.headers.get('location')
        new_id = int(location[location.rfind('/') + 1:])

        webhook['id'] = new_id
        return self.load(webhook)
        
    def create_page_webhook(self, action, callback_url, account_id=None, workspace_id=None,
        tag=None, page_id=None):
        """
        Create a webhook that responds to page actions

        :param action: The action to listen for.
        :param callback_url: The URL that Socialtext will send HTTP POSTs to.
        :param account_id: The ID of the :class:`Account` to listen for Page actions in.
        :param workspace_id: The ID of the :class:`Workspace` to listen for Page actions in.
        :param tag: The tag string to listen for Pages with this tag.
        :patam page_id: The ID of the :class:`Page` to listen for actions on.

        :rtype: :class:`Webhook`
        """
        details = {}
        if page_id:
            details['page_id'] = page_id
        if tag:
            details['tag'] = tag
        if action not in self.ACTION_PAGES:
            raise ValueError
        return self.create(action, callback_url, account_id=account_id,
            workspace_id=workspace_id, details=details)
        
    def create_signal_webhook(self, action, callback_url, account_id=None, group_id=None,
        user_id=None, tag=None):
        """
        Create a webhook that responds to signal actions

        :param action: The action to listen for. Currently only supports signal.create
        :param callback_url: The URL that Socialtext will send HTTP POSTs to.
        :param account_id: The ID of the :class:`Account` to listen for Signals in.
        :param group_id: The ID of the :class:`Group` to listen for Signals in.
        :param user_id: The ID of the :class:`User` to listen for Signals to.
        :param tag: The tag string to listen for in Signals.

        :rtype: :class:`Webhook`
        """
        if action not in self.ACTION_SIGNALS:
            raise ValueError
        details = {}
        if user_id:
            details["to_user"] = int(user_id)
        if tag:
            details["tag"] = tag
        return self.create("signal.create", callback_url, account_id=account_id,
            group_id=group_id, details=details)

    def delete(self, webhook):
        """
        Delete a webhook.

        :param webhook: The :class:`Webhook` (or ID of the webhook) to delete.
        """
        url = make_data_url("webhook", webhook_id=get_id(webhook))
        self._delete(url)
