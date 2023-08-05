from socialtext.resources.base import Manager, Resource, get_id
from socialtext.urls import make_data_url

class PageRevision(Resource):
    def __repr__(self):
        return "<PageRevision: %s@%s>" % (self.page_id, self.revision_id)
        
    def get_html(self):
        """
        Get the HTML representation of this page revision.
        
        :rtype: string of HTML
        """
        return self.manager.get_html(self)
        
    def get_wikitext(self):
        """
        Get the wikitext representation of this page revision.
        
        :rtype: string of wikitext
        """
        return self.manager.get_wikitext(self)
        
    def get_id(self):
        return self.revision_id
        
class PageRevisionManager(Manager):
    """
    Manage revisions of :class:`Page`. This
    manager is typically instantiated as an attribue
    on the :class:`Page` resource.
    """
    resource_class = PageRevision
    
    def __init__(self, api, page):
        self.api = api
        self.page = page
        
    def get(self, revision):
        """
        Get a specific :class:`PageRevision`.
        
        :param revision: The :class:`PageRevision` (or ID of the page revision) to get.
        
        :rtype: :class:`PageRevision`
        """
        url = make_data_url("revision",
            ws_name=self.page.workspace_name, page_name=get_id(self.page),
            revision_id = get_id(revision))
        return self._get(url)
        
    def get_wikitext(self, revision):
        """
        Get the wikitext representation of a specific page revision.
        
        :param revision: The :class:`PageRevision` (or ID of the page revision) to get.
                
        :rtype: string of wikitext.
        """
        url = make_data_url("revision",
            ws_name=self.page.workspace_name, page_name=get_id(self.page),
            revision_id = get_id(revision))
        
        headers = {'Accept' : 'text/x.socialtext-wiki'}
        resp, body = self.api.client.get(url, headers=headers)
        return body
        
    def get_html(self, revision):
        """
        Get the HTML representation of a specific page revision.
        
        :param revision: The :class:`PageRevision` (or ID of the page revision) to get.
                
        :rtype: string of HTML.
        """
        url = make_data_url("revision",
            ws_name=self.page.workspace_name, page_name=get_id(self.page),
            revision_id = get_id(revision))

        headers = {'Accept' : 'text/html'}
        resp, body = self.api.client.get(url, headers=headers)
        return body
        
        
    def list(self):
        """
        Get a list of all revisions for the associated :class:`Page`
        
        :rtype: list of :class:`PageRevision`
        """
        url = make_data_url("revisions",
            ws_name=self.page.workspace_name, page_name=get_id(self.page))
        return self._list(url)
        
    def create(self, *args, **kwargs):
        raise NotImplementedError
        
    def delete(self, *args, **kwargs):
        raise NotImplementedError
            
        
    