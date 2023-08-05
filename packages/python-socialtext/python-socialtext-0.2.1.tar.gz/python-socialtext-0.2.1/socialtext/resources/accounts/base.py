from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

from socialtext.resources.accounts.members import AccountMember, AccountMemberManager

class Account(Resource):

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.member_set = AccountMemberManager(self.manager.api, self)
    
    def __repr__(self):
        return "<Account: %s>" % self.account_id
        
    def get_id(self):
        """
        Get the ID that represents this account. The account_id is a
        required attribute.
        
        :rtype: string
        """
        assert hasattr(self, 'account_id'), "The account does not have an 'account_id' attribute."
        return self.account_id
        
class AccountManager(Manager):
    """
    Manage :class:`Account` resources.
    """
    resource_class = Account
    
    def list(self, expand=False, filter=""):
        """
        Get a list of :class:`Account` resources that the calling user has access to.
        
        :param expand: Get a full list of all accounts on the appliance. This requires
                    Business Admin permissions.
        :param filter: Return accounts whose name contains the filter value.
        :rtype: list of :class:`Account`
        """
        query = {}
        
        if expand:
            query['all'] = 1
            
        if filter:
            query['filter'] = filter
            
        url = make_data_url("accounts")
        
        return self._list(url, params=query)
        
    def get(self, account):
        """
        Get a specific account.
        
        :param account: The :class:`Account` (or ID of account) to get.
        :rtype: :class:`Account`
        """
        url = make_data_url("account", account_id=get_id(account))
        return self._get(url)
        
    def create(self, name):
        """
        Create a new account.
        
        :param name: The name of the new account.
        :rtype: :class:`Account`
        """
        data = { "name": name }
        
        url = make_data_url("accounts")
        
        resp, content = self.api.client.post(url, data=data)
        location = resp.headers.get('location')
        new_id = int(location[location.rfind('/') + 1:])
        return self.get(new_id)
        
    def delete(self, account):
        """
        Delete an account.
        
        :param account: The :class:`Account` (or ID of account) to delete.
        """
        raise NotImplementedError
