from socialtext.resources.base import Manager, Resource, get_id
from socialtext.urls import make_data_url

class AccountMember(Resource):
    def __repr__(self):
        return "<AccountMember: %s>" % self.user_id
        
    def delete(self):
        self.manager.delete(self)
    
    def get_id(self):
        return self.user_id

class AccountMemberManager(Manager):
    """
    Manage members of an account.
    """
    resource_class = AccountMember
    
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def get(self, user):
        """
        The Socialtext API does not support the GET operation on this URI.
        """
        raise NotImplementedError

    
    def create(self, user):
        """
        Add a user as a member to the account.
        
        :param username_or_id: The :class:User to add to the account
        """
        url = make_data_url("account_users",
            account_id=self.account.get_id())

        data = {
            "username": get_id(user)
        }
            
        resp, body = self.api.client.post(url, data=data)
