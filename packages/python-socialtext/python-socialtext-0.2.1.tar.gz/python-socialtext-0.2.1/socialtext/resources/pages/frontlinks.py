from socialtext.resources.base import Manager
from socialtext.urls import make_data_url

class PageFrontlinkManager(Manager):
    """
    Manage the pages that the related page links to.
    This manager is typically instantiated as an attribue
    on the :class:`Page` resource.
    
    .. note::
        
        All :class:`Page` instances returned by this manager
        will be attached to the related :class:`PageManager`.
    
    """
    def __init__(self, api, page):
        # avoid the recursive import reference
        from socialtext.resources.pages import Page
        self.resource_class = Page
        
        self.api = api
        self.page = page
        
    # this is a hack for now.
    # we need to set the resource's manager
    # to a regular PageManager so the caller
    # can take other actions such as delete() or get_wikitext()     
    def _list(self, url, **kwargs):
        resp, body = self.api.client.get(url, **kwargs)
        return [self.resource_class(self.page.manager, res) for res in body]
        
    def list(self, *args, **kwargs):
        """
        Get a list of pages that link to this page.
        
        Usage::
        
            page.frontlink_set.list()
            [<Page: 1>, <Page:2 >...]
        
        :rtype: list of :class:`Page`
        """
        url = make_data_url("frontlinks",
            ws_name = self.page.workspace_name,
            page_name = self.page.get_id()
        )
        return self._list(url)
        
    def create(self, *args, **kwargs):
        raise NotImplementedError
        
    def delete(self, *args, **kwargs):
        raise NotImplementedError
        
    def get(self, *args, **kwargs):
        raise NotImplementedError