try:
    all
except NameError:
    def all(iterable):
        return True not in (not x for x in iterable)


class Manager(object):
    """
    Managers interact with a  particular type of Resource (siganl, user, etc)
    and provide CRUD operations for them.
    """
    resource_class = None
    
    def __init__(self, api):
        self.api = api
        
    def _list(self, url, **kwargs):
        resp, body = self.api.client.get(url, **kwargs)
        return [self.resource_class(self, res) for res in body]
        
    def _get(self, url, **kwargs):
        resp, body = self.api.client.get(url, **kwargs)
        return self.resource_class(self, body)
        
    def _create(self, url, body, **kwargs):
        kwargs["data"] = body
        resp, body = self.api.client.post(url, **kwargs)
        return self.resource_class(self, body)
        
    def _delete(self, url, **kwargs):
        resp, body = self.api.client.delete(url, **kwargs)
        
    def _update(self, url, body, **kwargs):
        kwargs["data"] = body
        resp, body = self.api.client.put(url, **kwargs)
        
    def load(self, info):
        return self.resource_class(self, info)
        
    def load_from_webhook(self, webhook_payload):
        obj = webhook_payload.get('object', {})
        action = webhook_payload.copy()
        del action['object']
        return self.load(obj), BasicObject(action)


class BasicObject(object):
    """
    An object generated from a dictionary. The dictionary keys become the
    object attributes.
    """
    def __init__(self, info):
        self._info = info
        self._add_details(info)
        
    def _add_details(self, info):
        for (k, v) in info.iteritems():
            if isinstance(v, dict):
                setattr(self, k, BasicObject(v))
            else:
                setattr(self, k, v)
    
    def __getattr__(self, k):
        if k not in self.__dict__:
            raise AttributeError(k)
        else:
            return self.__dict__[k]
            
    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and k != 'manager')
        info = ', '.join('%s=%s' % (k, getattr(self, k)) for k in reprkeys)
        return '<%s %s>' % (self.__class__.__name__, info)


class Resource(BasicObject):
    """
    Represents a particular instance of a Socialtext Resource (Signal, User, etc.)
    """
    def __init__(self, manager, info):
        self.manager = manager
        super(Resource, self).__init__(info)
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._info == other._info
        
    def get_id(self):
        """
        The base implementation of get_id. Defaults to returing
        the Resources id attribute, if it exists.
        """
        assert hasattr(self, 'id'), "The %s does not have an 'id' attribute." % self.__class__.__name__
        return self.id
        
    def get(self):
        new = self.manager.get(self)
        self._add_details(new._info)


def get_id(obj):
    """
    Abstracts the common pattern of allow an object or an object's ID
    as a parameter when dealing with relationships.

    Returns the result of obj.get_id() or a string of the obj
    """
    return obj.get_id() if hasattr(obj, 'get_id') else str(obj)
