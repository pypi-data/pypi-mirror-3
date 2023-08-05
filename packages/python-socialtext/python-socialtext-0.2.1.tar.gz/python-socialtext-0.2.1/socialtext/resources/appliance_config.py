from socialtext.resources.base import Resource, Manager
from socialtext.urls import make_data_url


class ApplianceConfiguration(Resource):
    """
    A resource representing the configuration of the Socialtext appliance.
    """
    
    def get(self):
        """
        Get the Socialtext Appliance configuration. This will refresh
        the current object instance.
        """
        new = self.manager.get()
        return self._add_details(new._info)


class ApplianceConfigurationManager(Manager):
    """
    Manage the :class:`Configuration` resource.
    """
    resource_class = ApplianceConfiguration
    
    def get(self):
        """
        Get the Socialtext Appliance configuration.
        """
        url = make_data_url("config")
        return self._get(url)
