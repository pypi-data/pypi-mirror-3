import urllib

URL_SAFE_CHARS = '/,@;'
URL_QUERYARG_SEPERATOR = ';'

# The base URL for all API calls
DATA_URL = "/data"
# The base URL for all API calls to workspaces
WS_DATA_URL = DATA_URL + "/workspaces"

# A dictionary of DATA_URLS that require formatting arguments
DATA_URLS = {
    # PAGE DATA_URLS
    "pages"                 : WS_DATA_URL + "/%(ws_name)s/pages",
    "backlinks"             : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/backlinks",
    "frontlinks"            : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/frontlinks",
    "page"                  : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s",
    "pagetag"               : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/tags/%(tag)s",
    "pagetags"              : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/tags",
    "pagetaghistory"        : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/taghistory",
    "pagecomments"          : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/comments",
    "pageattachment"        : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/attachments/%(attachment_id)s",
    "pageattachments"       : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/attachments",
    "revisions"             : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/revisions",
    "revision"              : WS_DATA_URL + "/%(ws_name)s/pages/%(page_name)s/revisions/%(revision_id)s",
    
    # WORKSPACE DATA_URLS
    "breadcrumbs"           : WS_DATA_URL + "/%(ws_name)s/breadcrumbs",
    "taggedpages"           : WS_DATA_URL + "/%(ws_name)s/tags/%(tag)s/pages",
    "workspace"             : WS_DATA_URL + "/%(ws_name)s",
    "workspaces"            : WS_DATA_URL,
    "workspacehomepage"     : WS_DATA_URL + "/%(ws_name)s/homepage",
    "workspacetag"          : WS_DATA_URL + "/%(ws_name)s/tags/%(tag)s",
    "workspacetags"         : WS_DATA_URL + "/%(ws_name)s/tags",
    "workspaceattachment"   : WS_DATA_URL + "/%(ws_name)s/attachments/%(attachment_id)s",
    "workspaceattachments"  : WS_DATA_URL + "/%(ws_name)s/attachments",
    "workspaceuser"         : WS_DATA_URL + "/%(ws_name)s/users/%(user_id)s",
    "workspaceusers"        : WS_DATA_URL + "/%(ws_name)s/users",
    
    # PEOPLE, SIGNAL, & WEBHOOK DATA_URLS
    "accounts"              : DATA_URL + "/accounts",
    "account"               : DATA_URL + "/accounts/%(account_id)s",
    "account_users"         : DATA_URL + "/accounts/%(account_id)s/users",
    "account_user"         : DATA_URL + "/accounts/%(account_id)s/users/%(user)s",
    "groups"                : DATA_URL + "/groups",
    "group"                 : DATA_URL + "/groups/%(group_id)s",
    "config"                : DATA_URL + "/config",
    "people"                : DATA_URL + "/people",
    "person"                : DATA_URL + "/people/%(person_name)s",
    "person_tags"           : DATA_URL + "/people/%(person_name)s/tags",
    "person_photo"          : DATA_URL + "/people/%(person_name)s/photo",
    "signals"               : DATA_URL + "/signals",
    "signal"                : DATA_URL + "/signals/%(signal_id)s",
    "signal_hide"           : DATA_URL + "/signals/%(signal_id)s/hidden",
    "uploads"               : DATA_URL + "/uploads",
    "users"                 : DATA_URL + "/users",
    "user"                  : DATA_URL + "/users/%(user)s",
    "webhook"               : DATA_URL + "/webhooks/%(webhook_id)s",
    "webhooks"              : DATA_URL + "/webhooks",
}

def make_data_url(url_key, **kwargs):
    """
    Construct a url by using the formatting string in the DATA_URLS dictionary
    that is associated with the provided url_key. Items in the arguments_dict
    will be given to the URL formatter. The query_dict will be appended to the URL
    as a query string.
    
    Returns an ecoded string representation of the derived URL.
    """
    if not url_key in DATA_URLS.keys():
        raise ValueError("The url_key %s does not exist." % url_key)
    
    if kwargs:
        url = DATA_URLS[url_key] % kwargs
    else:
        url = DATA_URLS[url_key]
    url = urllib.quote(url, URL_SAFE_CHARS)
    return url
