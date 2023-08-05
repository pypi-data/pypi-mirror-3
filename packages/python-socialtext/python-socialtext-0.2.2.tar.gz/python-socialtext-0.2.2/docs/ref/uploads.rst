Uploads
=======

Upload files on your local filesystem or from a public URL to the Socialtext Appliance. Files are stored in a temporary staging area on the appliance.

Use this API to upload files so they can be attached to :class:`Signal` 
or :class:`Page` resources.

There is no :class:`Resource` for this API. The :class:`UploadManager`
only returns a hash-ID to represent the uploaded file.

.. seealso::
	For more detailed information about the Uploads URI, please see the `Socialtext documentation`__

	__ https://www.socialtext.net/st-rest-docs/index.cgi?data_uploads

Classes
-------

.. currentmodule:: socialtext.resources.uploads

.. autoclass:: UploadManager
   :members: create