The :mod:`socialtext` Python API
==================================

..  module:: socialtext
    :synopsis: A client for the Socialtext ReST API.

Examples
--------

    >>> from socialtext import Socialtext
    >>> st = Socialtext(url="https://st.example.com", username="joe", password="abc123")
    >>> st.pages.list('ws-name')
    [<Page: test_page_1>, <Page: test_page_2>]

    >>> st.users.list()
    [<User: ABC123>,
     <User: 987>,
     <User: ZYX444>,
     <User: 789>]

    >>> signal = st.signals.create("Hello world!")
    <Signal: 567>

    >>> signal.delete()

Classes
-------
   
..  currentmodule:: socialtext

..  autoclass:: Socialtext
    :members: impersonate
    
    .. attribute:: pages
    
        A :class:`PageManager` - query and create :class:`Page` resources
    
    .. attribute:: signals
    
        A :class:`SignalManager` - query and create :class:`Signal` resources.
        
    .. attribute:: users
    
        An :class:`UserManager` - query :class:`User` resources

    .. attribute:: webhooks

        A :class:`WebhookManager` - query and create :class:`Webhook` resources.
    
    .. attribute:: workspaces
    
        A :class:`WorkspaceManager` - query :class:`Workspace` resources.
    


For more information, see the reference:

.. toctree::
   :maxdepth: 2
   
   ref/index