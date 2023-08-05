from __future__ import absolute_import

from xmlrpclib import ServerProxy, Fault

from logging import getLogger
logger = getLogger('inifaction')

from inifaction import SECTIONS
from inifaction.items import convert


class API(object):
    def __init__(self, api):
        self.server = ServerProxy(api)
        self.session = None
        self.account = None

    def login(self, user, password, machine):
        self.session, self.account = self.server.login(user, password, machine)
        logger.info('Logged in with user "{user}" on machine "{machine}"'.format(
            user=self.account['username'], machine=self.account['web_server']))

    def list(self, key):
        result = getattr(self.server, 'list_' + key)(self.session)
        logger.info('{key} list done'.format(key=key.capitalize()))
        return result

    def exists(self, item):
        return any([ item[0] == s[item._fields[0]] for s in self.list(item.__section__) ])

    def _func(self, type, item):
        args = item.args(type)
        func = '{type}_{key}'.format(type=type, key=item.__name__)
        result = getattr(self.server, func)(self.session, *args)
        logger.info('{type} {key} "{arg}" done'.format(type=type.capitalize(), 
            key=item.__name__, arg=args[0]))
        return result

    def create(self, item):
        return self._func('create', item)

    def update(self, item):
        return self._func('update', item)

    def delete(self, item):
        return self._func('delete', item)

    def change_mailbox_password(self, item):
        key = 'change_mailbox_password'
        args = item.args(key)
        result = getattr(self.server, key)(self.session, *args)
        logger.info('{key} list done'.format(key=key.capitalize()))
        return result

    def delete_all(self, key):
        for status in self.list(key):
            item = convert(status, SECTIONS[key])
            try:
                self.delete(item)
            except Fault:
                pass
        return not self.list(key)
