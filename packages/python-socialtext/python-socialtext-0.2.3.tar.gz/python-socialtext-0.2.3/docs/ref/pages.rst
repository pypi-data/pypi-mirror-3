Pages
=======

Manage Socialtext Pages and their associated comments, backlinks, frontlinks, and tags.

.. seealso::
	For detailed information about the Pages URI, please see the `Socialtext Documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?data_workspaces_ws_pages

Resources
---------

.. currentmodule:: socialtext.resources.pages
             
.. autoclass:: Page
   :members: delete, get_html, get_id, name_to_id

   .. attribute:: backlink_set

		An instance of :class:`PageBacklinkManager`.
		
   .. attribute:: comment_set

	    An instance of :class:`PageCommentManager`.
		
   .. attribute:: frontlink_set

		An instance of :class:`PageFrontlinkManager`.
	
   .. attribute:: revision_set

		An instance of :class:`PageRevisionManager`.

   .. attribute:: tag_set
		
		An instance of :class:`PageTagManager`.

.. autoclass:: PageRevision
   :members: get_html, get_wikitext

.. autoclass:: PageTag
   :members: delete

Managers
--------

.. autoclass:: PageManager
   :members: get, get_html, list, delete, create

.. autoclass:: PageBacklinkManager
   :members: list

.. autoclass:: PageCommentManager
   :members: create

.. autoclass:: PageFrontlinkManager
   :members: list

.. autoclass:: PageRevisionManager
   :members: get, list

.. autoclass:: PageTagManager
   :members: create, delete, get, list