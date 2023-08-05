from socialtext.urls import make_data_url

class PageCommentManager(object):
    """
    Manage the comments associated with a page. This
    manager is typically instantiated as an attribue
    on the :class:`Page` resource.
    
    .. note::
    
        Only create() operations are supported.
    
    """
    def __init__(self, api, page):
        self.api = api
        self.page = page
    
    def create(self, comment):
        """
        Post a comment to the related page. This method
        has no return value but will raise an error if
        the operation fails.
        
        Usage::
        
            page.comment_set.create("This a *comment* using _wikitext_")
        
        :param comment: The wikitext body of the comment.
        """
        url = make_data_url("pagecomments",
            ws_name = self.page.workspace_name,
            page_name = self.page.get_id()
        )
        
        self.api.client.post(url, data=comment, headers={
            "Content-Type": "text/x.socialtext-wiki"
        })
        
    def list(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        raise NotImplementedError
