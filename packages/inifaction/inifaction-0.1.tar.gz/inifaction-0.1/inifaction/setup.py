from __future__ import absolute_import

from getpass import getpass

from inifaction import SECTIONS
from inifaction.api import API, Fault
from inifaction.config import Config, accept

from logging import getLogger
logger = getLogger('inifaction')

class Setup(object):
    class DoesNotExist(Exception):
        pass

    class DefinitionNeeded(Exception):
        pass

    def __init__(self, api, config):
        self.api = API(api)
        self.config = Config(config)
        self.config.check()

    def setup(self, sections=SECTIONS):
        self.login()
        for section in sections:
            if section not in SECTIONS:
                raise self.DoesNotExist('Possible sections are: {sections}'.format(
                    sections=', '.join(SECTIONS.keys())))
            try:
                getattr(self, section)()
            except Fault, msg:
                logger.error(msg)

    def login(self):
        user, password, machine = self.config.get_login()
        user = user or raw_input('User: ')
        password = password or getpass()
        if not machine and accept('Do you want to login in a machine?'):
            machine = raw_input('Machine: ')
        self.api.login(user, password, machine)

    def emails(self):
        for email in self.config.get_section('emails'):
            if self.api.exists(email):
                if accept('Email {email} already exists. Do you want to'
                    ' update it?'.format(email=email.email_address)): 
                    self.api.update(email)
            else:
                self.api.create(email)

    def mailboxes(self):
        for mailbox in self.config.get_section('mailboxes'):
            if self.api.exists(mailbox):
                if accept('Mailbox {mailbox} already exists, do you want to'
                        ' update it?'.format(mailbox=mailbox.mailbox)):
                    self.api.update(mailbox)
            else:
                self.api.create(mailbox)
            if mailbox.password:
                self.api.change_mailbox_password(mailbox)

    def domains(self):
        for domain in self.config.get_section('domains'):
            if self.api.exists(domain):
                if accept('Domain {domain} already exists, subdomains will be added.'
                        ' Do you want instead to delete it and create a new one?'.format(
                            domain=domain.domain)):
                            self.api.delete(domain)
            self.api.create(domain)

    def websites(self):
        ips = [ ip['ip'] for ip in self.api.list('ips') if\
                ip['machine'] == self.api.account['web_server'] ]
        for website in self.config.get_section('websites'):
            if not website.ip:
                if len(ips) is 1:
                    website = website._replace(ip=ips[0])
                else:
                    raise self.DefinitionNeeded('You have several IP adresses on machine'
                            ' {machine} ({ips}), define one'.format(
                                machine=self.api.account['web_server'],
                                ips=', '.join(ips)))
            if self.api.exists(website):
                if accept('Website {website} already exists. Do you want to update'
                        ' it?'.format(website=website.website_name)):
                    self.api.update(website)
            else:
                self.api.create(website)

    def apps(self):
        for app in self.config.get_section('apps'):
            if self.api.exists(app):
                if accept('Application {app} already exists. Do you want to'
                        ' delete it and create a new one?'.format(app=app.name)):
                    self.api.delete(app)
                else:
                    continue
            self.api.create(app)

    def dns_overrides(self):
        for override in self.config.get_section('dns_overrides'):
            if self.api.exists(override):
                if accept('DNS override {domain} already exists. Do you want'
                        ' to delete it and create a new one?'.format(
                            domain=override.domain)):
                    self.api.delete(override)
                else:
                    continue
            self.api.create(override)

    def dbs(self):
        for database in self.config.get_section('dbs'):
            if self.api.exists(database):
                if accept('Database {database} already exists. Do you want'
                        ' to delete it and create a new one?'.format(
                            database=database.name)):
                    self.api.delete(database)
                else:
                    continue
            self.api.create(database)
