from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

from socialtext.resources.workspaces.tags import WorkspaceTag, WorkspaceTagManager


class Workspace(Resource):
    def __init__(self, *args, **kwargs):
        super(Workspace, self).__init__(*args, **kwargs)
        self.tag_set = WorkspaceTagManager(self.manager.api, self)
        
    def __repr__(self):
        return "<Workspace: %s>" % self.name

    def delete(self):
        """
        Delete the current workspace.
        """
        self.manager.delete(self)
    
    def get_id(self):
        """
        Return the ID of the workspace. Defaults to the workspace name
        if present, otherwise returns the primary key (ID).

        :rtype: string
        """
        assert hasattr(self, 'name') or hasattr(self, 'id'), "The workspace does not have a 'name' or 'id' attribute"
        return self.name if self.name else self.id


class WorkspaceManager(Manager):
    """
    Manage :class:`Workspace` resources.
    """
    resource_class = Workspace
    
    PERM_AUTH_USER_ONLY = "authenticated-user-only"
    PERM_INTRANET = "intranet"
    PERM_PRIVATE = "member-only"
    PERM_PUBLIC = "public"
    PERM_PUBLIC_COMMENT_ONLY = "public-comment-only"
    PERM_PUBLIC_JOIN_TO_EDIT = "public-join-to-edit"
    PERM_PUBLIC_READ_ONLY = "public-read-only"
    PERM_SELF_JOIN = "self-join"
    
    PERM_CHOICES = [
        PERM_AUTH_USER_ONLY,
        PERM_INTRANET,
        PERM_PRIVATE,
        PERM_PUBLIC,
        PERM_PUBLIC_COMMENT_ONLY,
        PERM_PUBLIC_JOIN_TO_EDIT,
        PERM_PUBLIC_READ_ONLY,
        PERM_SELF_JOIN,
    ]
    
    def list(self):
        """
        Get a list of all workspaces.
        
        :rtype: list of :class:`Workspace`.
        """
        url = make_data_url("workspaces")
        return self._list(url)
        
    def get(self, ws):
        """
        Get a specific workspace.
        
        :param ws: The :class:`Workspace` (or name of the workspace) to get.
        :rtype: :class:`Workspace`.
        """
        url = make_data_url("workspace", ws_name=get_id(ws))
        return self._get(url)
        
    def create(self, name, title, account, cascade_css=False, clone_pages_from=None,
            customjs_uri="", customjs_name="", groups=[], permission_set=None, skin_name="",
            show_title_below_logo=False, show_welcome_message_below_logo=False):
        """
        Create a new workspace.
        
        :param name: The unique, URL-safe name for the workspace.
        :param title: The title of the workspace.
        :param account: The :class:`Account` (or Account ID) that the workspace should belong to.
        :param cascade_css: If True, the workspace's CSS will cascade.
        :param clone_pages_from: A :class:`Workspace` (or Workspace name) to clone pages from.
        :param customjs_uri: The URI of a custom JS script to be loaded when viewing workspace content.
        :param customjs_name: The name of the custom JS script.
        :param groups: A list of :class:`Group` (or Group ID) to invite to the workspace.
        :param permission_set: The permission set of the workspace. Must be one of PERM_CHOICES. Default is PERM_PRIVATE.
        :param show_title_below_logo: If True, the workspace title will be displayed below the logo.
        :param show_welcome_message_below_logo: If True, a welcome message will be displayed below the logo.
        :param skin_name: The name of the skin to use for the workspace.
        
        :rtype: :class:`Workspace`
        """
        ws = {
            "name": name,
            "title": title,
            "account_id": get_id(account),
        }
        
        if cascade_css:
            ws["cascade_css"] = 1
            
        if customjs_uri and customjs_name:
            ws["customjs_uri"] = customjs_uri
            ws["customjs_name"] = customjs_name
        elif (customjs_uri and not customjs_name) or (not customjs_uri and customjs_name):
            raise ValueError("You must provide both customjs_uri and customjs_name.")
        
        if skin_name:
            ws["skin_name"] = skin_name
            
        if show_welcome_message_below_logo:
            ws["show_welcome_message_below_logo"] = 1
            
        if show_title_below_logo:
            ws["show_title_below_logo"] = 1
            
        if clone_pages_from:
            ws["clone_pages_from"] = get_id(clone_pages_from)
            
        if permission_set:
            if permission_set in self.PERM_CHOICES:
                ws["permission_set"] = permission_set
            else:
                raise ValueError("The permission set %s is not one of the PERM_CHOICES" % permission_set)
        
        if groups:
            ws["groups"] = [{ "group_id" : get_id(g) } for g in groups]
            
        url = make_data_url("workspaces")
        resp, body = self.api.client.post(url, data=ws)
        return self.get(name)
        
    def delete(self, ws):
        """
        Delete a workspace in socialtext
        
        :param ws: The :class:`Workspace` (or name of the Workspace) to delete.
        """
        url = make_data_url("workspace", ws_name=get_id(ws))
        self._delete(url)
