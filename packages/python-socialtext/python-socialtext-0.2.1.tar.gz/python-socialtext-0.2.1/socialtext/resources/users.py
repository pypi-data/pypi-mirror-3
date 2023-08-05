from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url


class User(Resource):
    def __repr__(self):
        return "<User: %s>" % self.get_id()
    
    def delete(self):
        raise NotImplementedError
    
    def get_id(self):
        """
        Get the ID of this User.
        
        :rtype: str
        """
        if hasattr(self, "user_id"):
            return self.user_id
        elif hasattr(self, "username"):
            return self.username
        return ""
    
    def is_member_of_account(self, account):
        """
        Returns True if the user is a member of the provided account.
        
        :param account: The :class:`Account` (or ID of the Account) to check
        
        :rtype: bool
        """
        account_id = get_id(account)
        for acct in self.accounts:
            if acct['account_id'] == account_id:
                return True
        return False
    
    def is_member_of_group(self, group):
        """
        Returns True if the user is a member of the provided group.
        
        :param group: The :class:`Group` (or ID of the Group) to check
        
        :rtype: bool
        """
        group_id = get_id(group)
        for group in self.groups:
            if group['group_id'] == group_id:
                return True
        return False
    

class UserManager(Manager):
    """
    Manage :class:`User` resources.
    """
    ORDER_ALPHA = "alpha"
    ORDER_NEWEST = "newest"
    ORDER_CHOICES = [
        ORDER_ALPHA,
        ORDER_NEWEST
    ]
    
    resource_class = User
    
    def list(self, count=None, filter=None, offset=None, order=None,
        want_private_fields=False):
        """
        Get a list of all users
        
        :param count: Limit the number of users returned.
        :param filter: A search string to filter the search. Must be a prefix match.
        :param offset: Returns results starting at this offset from the beginning of the list.
        :param order: Sort the results by the order key. Must be one of the `ORDER_CHOICES`.
        :param want_private_fields: If True, the results will include private fields. The caller
                                    will need Business Admin priviledges, otherwise all private
                                    field values will default to None.
        :rtype: list of :class:`User`.
        """
        query = {}
        
        if count:
            query['count'] = int(count)
            
        if filter:
            query['filter'] = filter
            
        if offset:
            query['offset'] = int(offset)
            
        if order:
            if not order in self.ORDER_CHOICES:
                raise ValueError("The order key is invlaid. It must be one of UserManager.ORDER_CHOICS")
            query["order"] = order
                
        if want_private_fields:
            query['want_private_fields'] = 1
        
        url = make_data_url('users')
        
        return self._list(url, params=query)
    
    def get(self, user, minimal=False, want_private_fields=False, verbose=False):
        """
        Get a specific user
        
        :param user: The :class:`User` (or ID of the User) to get.
        :param minimal: If True, the minimal representation of the user will be returned.
        :param want_private_fields: If True, the User object will include private fields.
                                    The caller will need Business Admin priviledges,
                                    otherwise all private field values will default to None.
        :param verbose: If True, the User object will include all accounts and groups
                        to which the user belongs. The caller will need Business Admin privileges
                        to see the verbose information.
        :rtype: :class:`User`
        """
        query = {}
        
        if minimal:
            query['minimal'] = 1
        
        # we couldn't use the API's "all" parameter as a kwarg because "all"
        # is a Python reserved name.
        if verbose:
            query['all'] = 1
            
        if want_private_fields:
            query['want_private_fields'] = 1
        
        url = make_data_url('user', user=get_id(user))
        return self._get(url, params=query)
    
    def create(self, *args, **kwargs):
        raise NotImplementedError
    
    def delete(self, user):
        raise NotImplementedError
