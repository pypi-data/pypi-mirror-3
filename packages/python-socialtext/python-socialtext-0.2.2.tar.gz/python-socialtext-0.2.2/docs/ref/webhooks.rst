Webhooks
========

Query and create Socialtext Webhooks.

.. seealso::
	For detailed information about the Webhooks URI, please see the `Socialtext Documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?webhooks

Classes
-------

.. currentmodule:: socialtext.resources.webhooks

.. autoclass:: WebhookManager
   :members: get, list, delete, create, create_page_webhook, create_signal_webhook
   
             
.. autoclass:: Webhook
   :members: delete, get, get_id

   .. attribute:: id

        The unique identifier of this webhook.

   .. attribute:: creator_id

        The ID of the :class:`User` that created the webhook

   .. attribute:: class
   
        The webhook class, such as "page.tag" or "signal.create"
   
   .. attribute:: url
   
        The url that Socialtext will send the HTTP POST to when the webhook fires.

   .. attribute:: group_id
   
        The id of the :class:`Group` to which this webhook belongs.
   
   .. attribute:: details
   
        A :class:`BasicObject` referencing the details of the webhook. Attributes that may be present are 'user_id' for Signal Webhooks or 'tag' for Page Webhooks.
   
   .. attribute:: account_id
   
        The id of the :class:`Account` to which this webhook belongs.
   
   .. attribute:: workspace_id
   
        The id of the :class:`Workspace` to which this webhook belongs.
   