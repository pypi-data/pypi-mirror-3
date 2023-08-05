Signals
=======

Query and create Socialtext Signals to accounts, groups, and users.

.. seealso::
	For detailed information abou the Signals URI, please see the `Socialtext Documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?data_signals

Examples
--------

Here are some code examples illustrating the different Siganl operations:

Get
^^^

You can get a :class:`Signal` from the :class:`SignalManager`.::

  from socialtext import Socialtext

  st = Socialtext(ST_URL, ST_USER, ST_PASSWORD)

  signal = st.signals.get(1234) # get using an ID
  signal = st.signals.get(signal) # get using a Signal instnace
  signal.get() # refresh the instance

Create
^^^^^^

You can post basic Signals to your primary account or do advanced operations with attachments and cross-group postings.

Basic
`````

Just send a basic signal to your primary account::

  # send a basic signal
  signal = st.signals.create("Hello world!")

Mention a user
``````````````

You can include WikiText in your signals. Here is how you would mention another user::

  # you can use wikitext in the signal
  signal = st.signals.create("Hey, {user: joe@example.com}, did you do your TPS reports?")

Reply to a signal
`````````````````

You can reply to a signal by specifying the Signal ID or providing a :class:`Signal` instance

  
  # get the parent thread
  signal = st.signals.get(1234)

  # reply to the thread using a Signal instance
  reply = st.signals.create("Yes, I did do my TPS reports.", in_reply_to=signal)

  # reply to the thread using the Signal ID
  reply = st.signals.create("Yes, I did do my TPS reports.", in_reply_to=1234)

Send a private message
``````````````````````

To send a private message, you will need to know the recipient's User ID or provide a :class:`User` instance::

  
  # send a private message using the User ID
  private_msg = st.signals.create("This is a secret", recipient=1234)

  # send a private message with a User instance.
  recipient = st.users.get("joe@example.com")
  private_msg = st.signals.create("This is a secret". recipient=recipient)

Using attachments
`````````````````

You will need upload the desired files first using the :class:`UploadManager`::

  # some files to upload
  files = ['C:\hello_world.txt', 'http://url/for/image.png']

  # send them to /data/uploads
  uploads = [st.uploads.create(f) for f in files]

  # attach them to the signal
  signal = st.signals.create("I have attachments!", attachments=uploads)

Post to Accounts
````````````````

You can specify a list of accounts to post a Signal to::

  # post to a single group
  signal = st.signals.create("Hello account!", accounts=[1])

  # cross-group postings
  signal = st.signals.reate("Hello multiple groups.", accounts=[1,2,3])

Post to Groups
``````````````

You can specify a list of groups to post a Signal to::

  # post to a single group
  signal = st.signals.create("Hello group!", groups=[1])

  # cross-group postings
  signal = st.signals.reate("Hello multiple groups.", groups=[1,2,3])


Classes
-------

.. currentmodule:: socialtext.resources.signals

.. autoclass:: SignalManager
   :members: create, delete, get, hide, list 
   
             
.. autoclass:: Signal
   :members: delete, get_id, get_mentioned_user_ids, hide, is_user_mentioned

   .. attribute:: signal_id
   
        The signal's primary key.
   
   .. attribute:: body
   
        The full text of the signal as an HTML string.

   .. attribute:: at
   
        String representation of the time when the signal was created
   
   .. attribute:: user_id
   
        The id of the :class:`User` who created the signal.
   
   .. attribute:: best_full_name
   
        The name of the person who created the signal
   
   .. attribute:: annotations
   
        User defined metadata. See the `signals annotation`__ docs.
				
				__ https://www.socialtext.net/st-rest-docs/index.cgi?signals_annotations
   
   .. attribute:: account_ids
   
        A list of the ID for each account this signal was posted to.
   
   .. attribute:: group_ids
   
        A list of the ID for each group this signal was posted to.
   
   .. attribute:: in_reply_to
   
        A :class:`BasicObject` representing the signal that this is a reply to. The object has the attributes "signal_id", "uri", and "user_id"
  
   .. attribute:: mentioned_users

        A list of dictionaries representing the users who were mentioned in the Signal. Each dictionary contains the keys "id", "username", and "best_full_name".