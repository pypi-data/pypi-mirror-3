"""
Python bindings for the Socialtext REST API.
"""

VERSION = (0, 2, 3, "")

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])

import os
import ConfigParser

from distutils.util import strtobool

from socialtext.client import SocialtextClient
from socialtext.resources.accounts import AccountManager
from socialtext.resources.appliance_config import ApplianceConfigurationManager
from socialtext.resources.groups import GroupManager
from socialtext.resources.pages import PageManager
from socialtext.resources.signals import SignalManager
from socialtext.resources.uploads import UploadManager
from socialtext.resources.users import UserManager
from socialtext.resources.webhooks import WebhookManager
from socialtext.resources.workspaces import WorkspaceManager

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.socialtext/api.conf')

class Socialtext(object):
    """
    Top-level object to access the Socialtext API.

    Create an instance with your credentials::
    
        >>> st = Socialtext(server_url, username, password)

    Then call methods on its managers::
    
        >>> st.signals.list()
        ...
        >>> st.webhooks.list()
        ...

    """

    def __init__(self, **kwargs):
        self.config = self._get_config(kwargs)
        self.client = SocialtextClient(self.config)
        
        self.accounts = AccountManager(self)
        self.groups = GroupManager(self)
        self.pages = PageManager(self)
        self.appliance_config = ApplianceConfigurationManager(self)
        self.signals = SignalManager(self)
        self.uploads = UploadManager(self)
        self.users = UserManager(self)
        self.webhooks = WebhookManager(self)
        self.workspaces = WorkspaceManager(self)

    def impersonate(self, username):
        """
        Make API calls on behalf of the given user. Only calls to URIs
        in the /data/accounts or /data/workspaces routes are permitted.
        The API user must have impersonator permissions in the target
        :class:`Account` or target :class:`Workspace`.

        Example::

            # set the impersonation
            st.impersonate("joeuser")

            # clear the impersonation
            st.impersonate("")

        :param username: The username of the :class:`User` to impersonate.
        """
        self.client.impersonate(username)
        
    def _get_config(self, kwargs):
        """
        Get a Config object for this API client.
        
        Broken out into a seperate method so that the test client can easily
        mock it up.
        """
        return Config(
            config_file = kwargs.pop('config_file', None),
            env = kwargs.pop('env', None),
            overrides = kwargs,
        )
        
    def check_server_api_version(self):
        """
        Check the Socialtext appliance's API version against the version
        supported by this client.

        Returns True if API versions are in-sync.
        """
        appl_config = self.appliance_config.get()
        return appl_config.api_version == self.API_VERSION
        
        
class Config(object):
    """
    Encapsulates getting config from a number of places.

    Config passed in __init__ overrides config found in the environ, which
    finally overrides config found in a config file.
    """

    DEFAULTS = {
        'username': None,
        'password': None,
        'url': None,
        'user_agent': 'python-socialtext/%s' % __version__,
    }

    def __init__(self, config_file, env, overrides, env_prefix="SOCIALTEXT_"):
        config_file = config_file or DEFAULT_CONFIG_FILE
        env = env or os.environ

        self.config = self.DEFAULTS.copy()
        self.update_config_from_file(config_file)
        self.update_config_from_env(env, env_prefix)
        self.config.update(dict((k,v) for (k,v) in overrides.items() if v is not None))
        self.apply_fixups()

    def __getattr__(self, attr):
        try:
            return self.config[attr]
        except KeyError:
            raise AttributeError(attr)

    def update_config_from_file(self, config_file):
        """
        Update the config from a .ini file.
        """
        configparser = ConfigParser.RawConfigParser()
        if os.path.exists(config_file):
            configparser.read([config_file])

        # Mash together a bunch of sections -- "be liberal in what you accept."
        for section in ('global', 'socialtext'):
            if configparser.has_section(section):
                self.config.update(dict(configparser.items(section)))

    def update_config_from_env(self, env, env_prefix):
        """
        Update the config from the environ.
        """
        for key, value in env.iteritems():
            if key.startswith(env_prefix):
                key = key.replace(env_prefix, '').lower()
                self.config[key] = value

    def apply_fixups(self):
        """
        Fix the types of any updates based on the original types in DEFAULTS.
        """
        for key, value in self.DEFAULTS.iteritems():
            if isinstance(value, bool) and not isinstance(self.config[key], bool):
                self.config[key] = strtobool(self.config[key])
