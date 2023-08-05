import base64
import requests
import urllib
import urlparse

try:
    import json
except ImportError:
    import simplejson as json

# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

from socialtext import __version__ as api_version
from socialtext import exceptions

class SocialtextClient(object):
    
    def __init__(self, config):
        self.config = config
        self.on_behalf_of = ""
    
    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Accept', 'application/json')
        kwargs['headers']['User-Agent'] = self.config.user_agent
        
        if self.config.username and self.config.password:
            kwargs['headers']['authorization'] = self.authorization()

        if self.on_behalf_of:
            kwargs['headers']['X-On-Behalf-Of'] = self.on_behalf_of

        
        if 'data' in kwargs:
            kwargs['headers'].setdefault('Content-Type', 'application/json')
            kwargs['data'] = json.dumps(kwargs['data'])
        
        # we need to specially handle param values that are lists
        # to handle this properly, we generate the querystring
        # ourselves and send it to the requests module    
        if 'params' in kwargs:
            params = kwargs.get('params', {})
            
            for k,v in params.iteritems():
                if isinstance(v, list) and not isinstance(v, str):
                    params[k] = ",".join(v)
                    
            kwargs['params'] = urllib.urlencode(params, ",")
        
        resp = requests.request(method, url, **kwargs)
        
        if not resp.ok:
            raise exceptions.from_response(resp, resp.content)

        body = resp.content
        
        if body and kwargs['headers']['Accept'] == 'application/json':
            body = json.loads(body)
        
        return resp, body
    
    def authorization(self):
        return 'Basic ' + base64.b64encode("%s:%s" %
            (self.config.username, self.config.password))

    def impersonate(self, username):
        """
        Make HTTP requests on behalf of the provided user. The calling
        user must be an impersonator in the target account or workspace.
        Only requests to URIs in the /data/accounts or /data/workspaces
        routes are permitted.

        :param username: The username of the :class:`User` to impersonate.
                         If username is None or an empty string, the :class:`Client`
                         `on_behalf_of` attribute will be reset. 
        """
        if username:
            self.on_behalf_of = username
        else:
            self.on_behalf_of = ""
    
    def _get_full_url(self, path):
        return self.get_full_url(path)
        
    def get_full_url(self, path):
        return urlparse.urljoin(self.config.url, path)
    
    def _st_request(self, path, method, **kwargs):
        url = self._get_full_url(path)
        resp, body = self.request(url, method, **kwargs)
        return resp, body
    
    def get(self, url, **kwargs):
        """
        Send an HTTP GET request.

        :param url: The URL to GET.
        :param headers: A dictionary of HTTP headers for the request.
        :param params: A dictionary of params that will be added
                       as querystring arguments.
        """
        return self._st_request(url, 'GET', **kwargs)
    
    def post(self, url, **kwargs):
        """
        Send an HTTP POST request.

        :param url: The URL to POST to.
        :param data: The body of the POST request.
        :param files: A dictionary that maps filenames to file objects.
        :param headers: A dictionary of HTTP headers for the request.
        """
        return self._st_request(url, 'POST', **kwargs)
    
    def put(self, url, **kwargs):
        """
        Send an HTTP POST request.

        :param url: The URL to PUT to.
        :param data: The body of the PUT request.
        :param files: A dictionary that maps filenames to file objects.
        :param headers: A dictionary of HTTP headers for the request.
        """
        return self._st_request(url, 'PUT', **kwargs)
    
    def delete(self, url, **kwargs):
        """
        Send an HTTP DELETE request.

        :param url: The URL to PUT to.
        :param files: A dictionary that maps filenames to file objects.
        :param params: A dictionary of params that will be added
                       as querystring arguments.
        """
        return self._st_request(url, 'DELETE', **kwargs)
