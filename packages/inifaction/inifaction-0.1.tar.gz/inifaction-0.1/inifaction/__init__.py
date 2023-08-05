from os.path import join, dirname
from collections import OrderedDict
from inifaction.items import (Email, Mailbox, Domain, Website, App,
        DnsOverride, Database)

__all__ = ['config', 'items', 'api', 'setup']

API_URL = 'https://api.webfaction.com/'
CONFIG_SPEC = join(dirname(__file__), 'validation.ini')
CONFIG_TEMPLATE = join(dirname(__file__), 'template.ini')


SECTIONS = OrderedDict((
        ('domains', Domain),
        ('dns_overrides', DnsOverride),
        ('mailboxes', Mailbox),
        ('emails', Email),
        ('apps', App),
        ('websites', Website),
        ('dbs', Database),
        ))

NAMES = OrderedDict((
        ('domain', Domain),
        ('dns_override', DnsOverride),
        ('mailbox', Mailbox),
        ('email', Email),
        ('app', App),
        ('website', Website),
        ('db', Database),
        ))
