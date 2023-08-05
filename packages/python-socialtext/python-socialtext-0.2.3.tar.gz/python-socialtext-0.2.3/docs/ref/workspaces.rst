Workspaces
==========

Query Socialtext Workspaces

.. seealso::
	For detailed information about the Workspaces URI, please see the `Socialtext Documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?data_workspaces

Classes
-------

.. currentmodule:: socialtext.resources.workspaces

.. autoclass:: WorkspaceManager
   :members: get, list, delete, create
   
             
.. autoclass:: Workspace
   :members: get, get_id, delete

   More attributes are available if the user is a Business Administrator, however they are currently not `documented by Socialtext`__.

   __ https://www.socialtext.net/st-rest-docs/index.cgi?data_workspaces_ws

   .. attribute:: tag_set

		An instance of :class:`WorkspaceTagManager`

   .. attribute:: name
   
        The unique name of the workspace.
   
   .. attribute:: title
   
        The verbose name for the workspace.

   .. attribute:: pages_uri
   
        The fully qualified :class:`Page` collection URI

.. autoclass:: WorkspaceTagManager
   :members: get, list, delete, create