from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

from socialtext.resources.groups.trash import GroupTrashManager

class Group(Resource):
    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self._trash_manager = GroupTrashManager(self.manager.api, self)
    
    def __repr__(self):
        return "<Group: %s>" % self.get_id()
        
    def get_id(self):
        """
        Get the ID that represents this Group.
        
        :rtype: string
        """
        assert hasattr(self, 'group_id'), "This group does not have a `group_id` attribute."
        return self.group_id

    def trash(self, items):
        self._trash_manager.delete(items)
    
class GroupManager(Manager):
    """
    Manage :class:`Group` resources.
    """
    resource_class = Group
    
    DISCOVERABLE_PUBLIC = "public"
    DISCOVERABLE_EXCLUDE = "exclude"
    DISCOVERABLE_INCLUDE = "include"
    DISCOVERABLE_ONLY = "only"
    DISCOVERABLE_CHOICES = [
        DISCOVERABLE_PUBLIC,
        DISCOVERABLE_EXCLUDE,
        DISCOVERABLE_INCLUDE,
        DISCOVERABLE_ONLY
    ]
    
    PERMISSION_PRIVATE = "private"
    PERMISSION_SELF_JOIN = "self-join"
    PERMISSION_CHOICES = [
        PERMISSION_PRIVATE,
        PERMISSION_SELF_JOIN
    ]
    
    def get(self, group, show_members=False, can_update_perms=False):
        """
        Get a specific :class:`Group`.
        
        :param group: The :class:`Group` (or ID of a Group) to get.
        :param show_members: Include a list of members. Warning, this is an expensive operation.
        :param can_update_perms: If True, an additional attribute will be added to the resource
                                 to indicate whether or not the calling user can update the
                                 group permissions.
        
        :rtype: :class:`Group`
        """
        query = {}
        
        if show_members:
            query["show_members"] = 1
        
        if can_update_perms:
            query["can_update_perms"] = 1
            
        url = make_data_url("group", group_id=get_id(group))
        
        return self._get(url, params=query)
        
    def list(self, expand=False, filter="", discoverable=None, show_members=False):
        """
        Get a list of :class:`Group` resources that the calling user has access to.
        
        :param expand: Get a full list of all groups on the appliance. The calling user must be
                       a Business Admin.
        :param filter: Limit the list to groups to those who match the filter expression.
        :param discoverable: Limit the groups list to how they are discoverable by the user.
                             Must be one of `DISCOVERABLE_CHOICES`.
        :param show_members: Each resource will include a list of members. Warning: This is an expensive call.
        
        :rtype: list of :class:`Group`
        """
        query = {}
        
        if expand:
            query["all"] = 1
            
        if filter:
            query["filter"] = filter
            
        if discoverable:
            if discoverable in self.DISCOVERABLE_CHOICES:
                query["discoverable"] = discoverable
            else:
                raise ValueError("The discoverable kwarg must be one of the DISCOVERABLE_CHOICES")
            
        if show_members:
            query["show_members"] = 1
            
        url = make_data_url("groups")
        
        return self._list(url, params=query)
        
    def create(self, name, account=None, description="", permission_set=None):
        """
        Create a new native group.
        
        :param name: The name of the group.
        :param account: The :class:`Account` (or ID of account) the group should belong to.
                        If None, the group will belong to your default account.
        :param description: Text describing the group.
        :param permission_set: Indicates whether or not the group is self_join or private.
                               Must be one of PERMISSION_CHOICES. Default is `self_join`.
        """
        data = {}
        data["name"] = name
        
        if account:
            data["account_id"] = get_id(account)
        
        if description:
            data["description"] = description
            
        if permission_set:
            if permission_set in self.PERMISSION_CHOICES:
                data["permission_set"] = permission_set
            else:
                raise ValueError("The permission_set kwarg must be one of the PERMISSION_CHOICES")
                
        url = make_data_url("groups")
        resp, content = self.api.client.post(url, data=data)
        location = resp.headers.get('location')
        new_id = int(location[location.rfind('/') + 1:])
        return self.get(new_id)
    
    def delete(self, group):
        raise NotImplementedError
