from socialtext.resources.base import Manager, Resource, get_id
from socialtext.urls import make_data_url

class SignalLike(Resource):
    def __repr__(self):
        return "<SignalLike: %s>" % self.best_full_name
        
    def delete(self):
        self.manager.delete(self)
    
    def get_id(self):
        return self.user_id

class SignalLikeManager(Manager):
    """
    Manage likes for a Signal.
    """
    resource_class = SignalLike
    
    def __init__(self, api, signal):
        self.api = api
        self.signal = signal
    
    def get(self, tag):
        raise NotImplementedError()
        
    def create(self):
        """
        Like the tag that this manager belongs to.
        """
        url = make_data_url("signallike",
            signal_id=get_id(self.signal), user_id=self.api.config.username)
            
        self._update(url, None)
        
    def list(self):
        """
        Get a list of users who like this Signal.
        
        :rtype: list of :class:`SignalLiker`
        """
        url = make_data_url("signallikes", signal_id=get_id(self.signal))
        return self._list(url)
    
    def delete(self):
        """
        Unlike the provided Signal.
        
        :param tag: A :class:`Signal` (or Signal ID) to unlike.
        """
        url = make_data_url("signallike",
           signal_id=get_id(self.signal), user_id=self.api.config.username)
        self._delete(url)
