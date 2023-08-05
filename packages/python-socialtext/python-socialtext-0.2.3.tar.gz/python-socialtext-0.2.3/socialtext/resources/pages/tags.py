from socialtext.resources.base import Manager, Resource, get_id
from socialtext.urls import make_data_url

class PageTag(Resource):
    """
    A representation of a tag on a :class:`Page`.
    """
    def __repr__(self):
        return "<PageTag: %s>" % self.name
        
    def delete(self):
        """
        Remove this tag from the :class:`Page`.
        """
        self.manager.delete(self)
    
    def get_id(self):
        return self.name

class PageTagManager(Manager):
    """
    Manage the tags on the related page.
    """
    resource_class = PageTag
    
    def __init__(self, api, page):
        self.api = api
        self.page = page
    
    def get(self, tag):
        """
        Get a specific tag on a page.
        
        :param tag: A :class:`PageTag` (or tag string) to get
        
        :rtype: :class:`PageTag`
        """
        if isinstance(tag, PageTag):
            tag = get_id(tag)
            
        url = make_data_url("pagetag",
            ws_name=self.page.workspace_name, page_name=get_id(self.page), tag=tag)
        return self._get(url)
        
    def create(self, tag):
        """
        Add a specific tag to a page.
        
        :param tag: The tag to add to the page.
        
        :rtype: :class:`PageTag`
        """
        url = make_data_url("pagetag",
            ws_name=self.page.workspace_name, page_name=get_id(self.page), tag=get_id(tag))
            
        self._update(url, None)
        return self.get(tag)
        
    def list(self):
        """
        Get a list of tags for the page.
        
        :rtype: list of :class:`PageTag`
        """
        url = make_data_url("pagetags",ws_name=self.page.workspace_name, page_name=get_id(self.page))
        return self._list(url)
    
    def delete(self, tag):
        """
        Delete a :class:`PageTag` from a page.
        
        :param tag: A :class:`PageTag` (or tag string) to delete.
        """
        url = make_data_url("pagetag",
            ws_name=self.page.workspace_name, page_name=get_id(self.page), tag=get_id(tag))
        self._delete(url)
