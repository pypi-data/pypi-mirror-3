"""
Command-line utility to access the Socialtext REST API.
"""

import argparse
import os
import prettytable
import socialtext
import sys
import textwrap

from socialtext import exceptions

# Decorator for args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator

class CommandError(Exception):
    pass
    
class SocialtextShell(object):
    _api_class = socialtext.Socialtext
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog = "socialtext",
            description = __doc__.strip(),
            epilog = 'See "socialtext help COMMAND" for help on a specific command.',
            add_help = False,
            formatter_class = SocialtextHelpFormatter
        )
        
        self.parser.add_argument('-f', '--config-file',
            metavar = 'PATH',
            default = None,
            help = 'Path to config file (default: ~/.socialtext/api.conf)')
        
        self.parser.add_argument('--username',
            default = None,
            help = 'Socialtext username. Required if not in a config file/environ.')
            
        self.parser.add_argument('--password',
            default = None,
            help='Socialtext password. Required if not in a config file/environ.')
            
        self.parser.add_argument('--url',
            default = None,
            help='Socialtext url. Required if not in a config file/environ.')
        
        # Subcommands
        subparsers = self.parser.add_subparsers(metavar='<subcommand>')
        self.subcommands = {}
        
        # Everything that's do_* is a subcommand.
        for attr in (a for a in dir(self) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(self, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])
            
            subparser = subparsers.add_parser(command, 
                help = help,
                description = desc,
                add_help=False,
                formatter_class = SocialtextHelpFormatter
            )
            subparser.add_argument('-h', '--help',
                action = 'help',
                help = argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)
            
    def main(self, argv):
        # Parse args and call whatever callback was selected
        args = self.parser.parse_args(argv)
        
        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        
        self.st = self._api_class(
            config_file = args.config_file,
            username = args.username,
            password = args.password,
            url = args.url,
        )
        
        if not self.st.config.username:
            raise CommandError("You must provide a username, either via "
                               "--username, env[SOCIALTEXT_USERNAME], "
                               " or a config file.")
        if not self.st.config.password:
            raise CommandError("You must provide a password, either via "
                               "--password, env[SOCIALTEXT_PASSWORD], "
                               " or a config file.")
                               
        if not self.st.config.url:
            raise CommandError("You must provide a Socialtext appliance URL via"
                               "--url, env[SOCIALTEXT_URL], or a config file.")
        
        args.func(args)
        
    @arg('command', metavar='<subcommand>', nargs='?', help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise CommandError("'%s' is not a valid subcommand." % args.command)
        else:
            self.parser.print_help()

    def do_whoami(self, args):
        print "You are %s on %s" % (self.st.config.username, self.st.config.url)
            
############
# ACCOUNTS #
############
            
    def do_account_list(self, args):
        """
        Print a list of available accounts.
        """
        print_list(self.st.accounts.list(), ['Account ID', 'Account Name'])
        
    @arg("account_id", metavar="<account_id>", help="The ID of the Account.")
    def do_account_show(self, args):
        """
        Show details about a particular account.
        """
        acct = self._get_account(args.account_id)
        print_dict(acct._info)

###################
# ACCOUNT MEMBERS #
###################

    @arg('account', metavar='<account>', help="The ID of the Account.")
    @arg('username', metavar='<username>', help="The username of the User to add.")
    def do_account_add_member(self, args):
        """
        Add the user to the specified account
        """
        print "Getting account"
        acct = self._get_account(args.account)
        print "Adding user to account"
        acct.member_set.create(args.username)
        print "%s is now a member of %s" % (args.username, acct.name)


        
##########
# GROUPS #
##########
            
    def do_group_list(self, args):
        """
        Print a list of groups.
        """
        print_list(self.st.groups.list(), ['Group ID', 'Name'])
        
    @arg('group_id', metavar='<group_id>', help="The ID of the Group.")
    def do_group_show(self, args):
        """
        Show details about a particular group.
        """
        group_id = args.group_id
        print_dict(self.st.groups.get(group_id)._info)
        
#########
# PAGES #
#########
        
    @arg('workspace', metavar='<workspace>', help='The workspace name.')   
    def do_page_list(self, args):
        """
        Print a list of pages in a given workspace.
        """
        ws = args.workspace
        print_list(self.st.pages.list(ws), ['Page ID'])

    @arg('workspace', metavar='<workspace>', help='The workspace name.')
    @arg('page_id', metavar='<page_id>', help='The ID of the page.')
    def do_page_show(self, args):
        """
        Show details about a particular page.
        """
        pg = self._get_page(args.workspace, args.page_id)
        print_dict(pg._info)
        
    @arg('workspace', metavar='<workspace>', help='The workspace name.')
    @arg('page_id', metavar='<page_id>', help='The ID of the page.')
    def do_page_backlinks_list(self, args):
        """
        Print a list of backlinks to a particular page.
        """
        pg = self._get_page(args.workspace, args.page_id)
        print_list(pg.backlink_set.list(), ['Page ID'])

#########
# USERS #
#########

    @arg('user', metavar='<user>', help="The username or user ID.")
    def do_user_detail(self, args):
        user = self._get_user(args.user)
        data = {
            "id": user.user_id,
            "username": user.username,
            "display_name": user.display_name,
            "last_login": user.last_login_datetime,
            "primary_account_id": user.primary_account_id,
            "primary_account_name": user.primary_account_name,
            "email_address": user.email_address,
            "is_technical_admin": user.is_technical_admin,
            "is_business_admin": user.is_business_admin,
            "created_at": user.creation_datetime

        }
        print_dict(data)
        
        
##############
# WORKSPACES #
##############
    
    def do_workspace_list(self, args):
        """
        Print a list of available workspaces.
        """
        print_list(self.st.workspaces.list(), ['Title', 'Name'])
    
    @arg('workspace', metavar='<workspace>', help='The workspace name.')    
    def do_workspace_show(self, args):
        """
        Show details about a particular workspace.
        """
        ws = self._get_workspace(args.workspace)
        print_dict(ws._info)
        
    @arg('workspace', metavar='<workspace>', help='The workspace name.')
    def do_workspace_delete_examples(self, args):
        """
        Delete the example pages from a workspace.
        """
        ws = args.workspace
        deleted = []
        pages = self.st.pages.list(ws)
        
        for p in pages:
            if p.page_id.find('example') == 0:
                self.st.pages.delete(p)
                deleted.append(p)
                
        print_list(deleted, ['Page ID'])
        
###########
# HELPERS #
###########
        
    def _get_account(self, account):
        return self._get_resource(self.st.accounts, account)
        
    def _get_page(self, ws, page):
        return self._get_resource(self.st.pages, page, ws=ws)

    def _get_user(self, username_or_id):
        return self._get_resource(self.st.users, username_or_id)
        
    def _get_workspace(self, ws):
        return self._get_resource(self.st.workspaces, ws)
            
    def _get_resource(self, manager, name_or_id, **kwargs):
        try:
            return manager.get(name_or_id, **kwargs)
        except exceptions.NotFound, exc:
            raise CommandError("No %s with a name or ID of '%s' exists."
                % (manager.resource_class.__name__.lower(), name_or_id))


class SocialtextHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(SocialtextHelpFormatter, self).start_section(heading)


###########
# HELPERS #
###########

def print_list(objs, fields, formatters={}):
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                row.append(getattr(o, field.lower().replace(' ', '_'), ''))
        pt.add_row(row)

    pt.printt(sortby=fields[0])

def print_dict(d):
    pt = prettytable.PrettyTable(['Property', 'Value'], caching=False)
    pt.aligns = ['l', 'l']
    [pt.add_row(list(r)) for r in d.iteritems()]
    pt.printt(sortby='Property')

def main():
    try:
        SocialtextShell().main(sys.argv[1:])
    except CommandError, e:
        print >> sys.stderr, e
        sys.exit(1)
        
        