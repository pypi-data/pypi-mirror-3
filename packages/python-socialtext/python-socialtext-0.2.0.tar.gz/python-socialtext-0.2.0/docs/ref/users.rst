Users
=====

Query Socialtext Users

.. seealso::
	For more detailed information about the Users URI, please see the `Socialtext documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?data_users

Classes
-------

.. currentmodule:: socialtext.resources.users

.. autoclass:: UserManager
   :members: get, list, delete, create
   
             
.. autoclass:: User
   :members: get, get_id, delete, is_member_of_account, is_member_of_group

   .. note::
   		The User attributes are complicated. We are working to document the different variations. In the mean time, please see the `Socialtext User JSON Representation`__ documentation for more information.

   __ https://www.socialtext.net/st-rest-docs/index.cgi?json_user_representation