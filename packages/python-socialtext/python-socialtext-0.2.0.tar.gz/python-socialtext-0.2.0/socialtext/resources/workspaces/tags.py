from socialtext.resources.base import Manager, Resource, get_id
from socialtext.urls import make_data_url

class WorkspaceTag(Resource):
    def __repr__(self):
        return "<WorkspaceTag: %s>" % self.name
        
    def delete(self):
        self.manager.delete(self)
    
    def get_id(self):
        return self.name

class WorkspaceTagManager(Manager):
    """
    Manage tags for a page.
    """
    resource_class = WorkspaceTag
    
    def __init__(self, api, ws):
        self.api = api
        self.workspace = ws
    
    def get(self, tag):
        """
        Get a specific tag that is in the workspace.
        
        :param tag: A :class:`WorkspaceTag` (or tag string) to get
        
        :rtype: :class:`WorkspaceTag`
        """
        if isinstance(tag, WorkspaceTag):
            tag = get_id(tag)
            
        url = make_data_url("workspacetag",
            ws_name=self.workspace.name, tag=tag)
        return self._get(url)
        
    def create(self, tag):
        """
        Add a specific tag to a workspace.
        
        :param tag: The tag to add to the page.
        
        :rtype: :class:`WorkspaceTag`
        """
        url = make_data_url("workspacetag",
            ws_name=self.workspace.name, tag=tag)
            
        self._update(url, None)
        return self.get(tag)
        
    def list(self):
        """
        Get a list of tags for the workspace.
        
        :rtype: list of :class:`WorkspaceTag`
        """
        url = make_data_url("workspacetags",ws_name=self.workspace.name)
        return self._list(url)
    
    def delete(self, tag):
        """
        Delete a :class:`Tag` from a workspace.
        
        .. warning::
            This will remove the tag from ALL the pages it belongs to.
        
        :param tag: A :class:`WorkspaceTag` (or tag string) to delete.
        """
        url = make_data_url("workspacetag",
            ws_name=self.workspace.name, tag=get_id(tag))
        self._delete(url)
