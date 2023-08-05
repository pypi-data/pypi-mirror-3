from xmlrpclib import boolean
from collections import namedtuple


_Email = namedtuple('Email', (
    'email_address', 
    'targets', 
    'autoresponder_on', 
    'autoresponder_subject', 
    'autoresponder_message', 
    'autoresponder_from',
    'script_machine', 
    'script_path',
    ))

_Mailbox = namedtuple('Mailbox', (
    'mailbox', 
    'enable_spam_protection', 
    'discard_spam',
    'spam_redirect_folder', 
    'use_manual_procmailrc', 
    'manual_procmailrc',
    ))

_Domain = namedtuple('Domain', (
    'domain', 
    'subdomains',
    ))

_Website = namedtuple('Website', (
    'name', 
    'ip', 
    'https', 
    'subdomains', 
    'apps',
    ))

_App = namedtuple('App', (
    'name', 
    'type', 
    'autostart', 
    'extra_info',
    'script_code',
    ))

_DnsOverride = namedtuple('DnsOverride', (
    'domain', 
    'a_ip', 
    'cname', 
    'mx_name',
    'mx_priority', 
    'spf_record',
    ))

_Database = namedtuple('Database', (
    'name', 
    'db_type', 
    'password',
    ))


class Item(object):
    def args(self, action=None):
        replacements = {}
        for field in self._fields:
            value = getattr(self, field)
            if type(value) == bool:
                replacements[field] = boolean(value)
        return self._replace(**replacements)

    @classmethod
    def from_status(cls, **kwargs):
        filtered = {}
        for field in cls._fields:
            if field in kwargs:
                filtered[field] = kwargs[field]
            else:
                filtered[field] = None
        return cls(**filtered)

    @classmethod
    def from_config(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def _make(self, *args, **kwargs):
        raise NotImplemented


class Email(_Email, Item):
    __name__ = 'email'
    __section__ = 'emails'
    __doc__ = _Email.__doc__
    def args(self, action=None):
        args = super(Email, self).args(action)
        if action == 'create' or action == 'update':
            return args._replace(targets=', '.join(self.targets))
        elif action == 'delete':
            return args.email_address,
        return args


class Mailbox(_Mailbox, Item):
    __name__ = 'mailbox'
    __section__ = 'mailboxes'
    __doc__ = _Mailbox.__doc__
    password = ''

    def args(self, action=None):
        args = super(Mailbox, self).args(action)
        if action == 'change_mailbox_password':
            return args.mailbox, self.password
        elif action == 'delete':
            return args.mailbox,
        return args

    @classmethod
    def from_config(cls, *args, **kwargs):
        password = kwargs.pop('password') 
        mailbox = cls(*args, **kwargs)
        mailbox.password = password
        return mailbox

    def _replace(self, *args, **kwargs):
        new = super(Mailbox, self)._replace(*args, **kwargs)
        new.password = self.password
        return new

class Domain(_Domain, Item):
    __name__ = 'domain'
    __section__ = 'domains'
    __doc__ = _Domain.__doc__
    def args(self, action=None):
        args = super(Domain, self).args(action)
        if action == 'create':
            return tuple(args[:-1]) + tuple(args[-1])
        elif action == 'delete':
            return args.domain,
        return args

    
class Website(_Website, Item):
    __name__ = 'website'
    __section__ = 'websites'
    __doc__ = _Website.__doc__
    def args(self, action=None):
        args = super(Website, self).args(action)
        if action == 'create' or action == 'update':
            return tuple(args[:-1]) + tuple(args[-1])
        elif action == 'delete':
            return args.name,
        return args

    @classmethod
    def from_config(cls, *args, **kwargs):
        apps = kwargs.pop('apps', {})
        return cls(apps=apps.items(), *args, **kwargs)


class App(_App, Item):
    __name__ = 'app'
    __section__ = 'apps'
    __doc__ = _App.__doc__
    def args(self, action=None):
        args = super(App, self).args(action)
        if action == 'delete':
            return args.name,
        return args


class DnsOverride(_DnsOverride, Item):
    __name__ = 'dns_override'
    __section__ = 'dns_overrides'
    __doc__ = _DnsOverride.__doc__
    pass


class Database(_Database, Item):
    __name__ = 'db'
    __section__ = 'dbs'
    __doc__ = _DnsOverride.__doc__
    def args(self, action=None):
        args = super(Database, self).args(action)
        if action == 'delete':
            return args.name, args.db_type
        return args


def convert(status, item_type):
    return item_type.from_status(**status)
