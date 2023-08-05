from socialtext.resources.base import Manager, Resource, get_id
from socialtext.resources.users import User
from socialtext.resources.workspaces import Workspace
from socialtext.urls import make_data_url

class GroupTrashManager(Manager):

	def __init__(self, api, group):
		self.api = api
		self.group = group

	def create(self):
		raise NotImplementedError()

	def delete(self, items):
		"""
		Remove the membership for each of the items.

		:param items: A list of class:`User` or class:`Workspace` objects
		"""

		url = make_data_url("grouptrash", group_id=get_id(self.group))
		items_to_trash = []

		for item in items:
			if isinstance(item, User):
				items_to_trash.append(dict(user_id=get_id(item)))
			elif isinstance(item, Workspace):
				items_to_trash.append(dict(workspace_id=get_id(item.workspace_id)))
			else:
				raise ValueError("%s is neither a Group nor Workspace." % item)
		
		resp, client = self.api.client.post(url, data=items_to_trash)


	def get(self):
		raise NotImplementedError()

	def list(self):
		raise NotImplementedError()