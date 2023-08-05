from __future__ import with_statement

import unittest
from os.path import join, dirname
from validate import ValidateError

from inifaction.api import API
from inifaction.config import Config, accept
from inifaction.setup import Setup
from inifaction import API_URL, SECTIONS, NAMES
from inifaction.items import (Email, Mailbox, Domain, Website, App, DnsOverride,
        Database)

import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        with open(join(dirname(__file__), 'config.ini')) as test_file:
            self.config = Config(test_file)

    def test_check(self):
        self.assertTrue(self.config.check())
        self.config['emails']['example@email.net']['targets'] = False
        with self.assertRaises(ValidateError):
            self.config.check()

    def test_login(self):
        self.assertEqual(self.config.get_login(), config.login)

    def test_sections(self):
        for section, name in zip(SECTIONS.keys(), NAMES.keys()):
            self.assertEqual(tuple(self.config.get_section(section)[0]), tuple(getattr(config, name)))

accepted = accept('Running the TestAPI or TestSetup tests will delete all your configuration '
        'from Webfaction servers. Do you want to continue?')

class TestAPI(unittest.TestCase):
    def setUp(self):
        if not accepted:
            self.skipTest('TestAPI skiped')
        self.api = API(API_URL)

    def test_login(self):
        user, password, machine = config.login
        self.api.login(user, password, machine)
        self.assertEqual(self.api.account['username'], user)
        self.assertEqual(self.api.account['web_server'], machine)

    def test_mailbox(self):
        self.api.login(*config.login)

        self.api.delete_all('mailboxes')
        self.assertEqual(len(self.api.list('mailboxes')), 1)
        self.assertFalse(self.api.exists(config.mailbox))

        self.api.create(config.mailbox)
        self.assertTrue(self.api.exists(config.mailbox))

        mailbox = config.mailbox._replace(enable_spam_protection=True)
        self.api.update(mailbox)
        self.assertTrue(self.api.exists(mailbox))

        self.api.change_mailbox_password(mailbox)

        self.api.delete(mailbox)
        self.assertFalse(self.api.exists(mailbox))

    def test_email(self):
        self.api.login(*config.login)
        # Create target mailbox and domain
        self.api.delete_all('mailboxes')
        self.api.create(config.mailbox)
        self.api.delete_all('domains')
        self.api.create(config.domain)

        self.assertTrue(self.api.delete_all('emails'))
        self.assertFalse(self.api.exists(config.email))

        self.api.create(config.email)
        self.assertTrue(self.api.exists(config.email))

        email = config.email._replace(targets=('second_target@email.net',))
        self.api.update(email)
        self.assertTrue(self.api.exists(email))

        self.api.delete(email)
        self.assertFalse(self.api.exists(email))

    def test_domain(self):
        self.api.login(*config.login)

        self.assertTrue(self.api.delete_all('domains'))
        self.assertFalse(self.api.exists(config.domain))

        self.api.create(config.domain)
        self.assertTrue(self.api.exists(config.domain))

        domain = config.domain._replace(subdomains=('www', 'doc'))
        self.api.create(domain)
        self.assertTrue(self.api.exists(domain))

        self.api.delete(domain)
        self.assertFalse(self.api.exists(domain))

    def test_app(self):
        self.api.login(*config.login)

        self.assertTrue(self.api.delete_all('apps'))
        self.assertFalse(self.api.exists(config.app))

        self.api.create(config.app)
        self.assertTrue(self.api.exists(config.app))

        self.api.delete(config.app)
        self.assertFalse(self.api.exists(config.app))

    def test_website(self):
        self.api.login(*config.login)
        # Create website domain and app
        self.api.delete_all('domains')
        self.api.create(config.domain)
        self.api.delete_all('apps')
        self.api.create(config.app)

        self.assertTrue(self.api.delete_all('websites'))
        self.assertFalse(self.api.exists(config.website))

        self.api.create(config.website)
        self.assertTrue(self.api.exists(config.website))

        website = config.website._replace(subdomains=['www.email.net', 'email.net'])
        self.api.update(website)
        self.assertTrue(self.api.exists(website))

        self.api.delete(website)
        self.assertFalse(self.api.exists(website))

    def test_dns_override(self):
        self.api.login(*config.login)

        self.assertTrue(self.api.delete_all('dns_overrides'))
        self.assertFalse(self.api.exists(config.dns_override))

        self.api.create(config.dns_override)
        self.assertTrue(self.api.exists(config.dns_override))

        self.api.delete(config.dns_override)
        self.assertFalse(self.api.exists(config.dns_override))

    def test_database(self):
        self.api.login(*config.login)

        self.assertTrue(self.api.delete_all('dbs'))
        self.assertFalse(self.api.exists(config.db))

        self.api.create(config.db)
        self.assertTrue(self.api.exists(config.db))

        self.api.delete(config.db)
        self.assertFalse(self.api.exists(config.db))

class TestSetup(unittest.TestCase):
    def setUp(self):
        if not accepted:
            self.skipTest('TestSetup skiped')
        with open(join(dirname(__file__), 'config.ini')) as test_file:
            self.setup = Setup(API_URL, test_file)

    def test_setup(self):
        self.setup.login()
        for section in SECTIONS:
            self.setup.api.delete_all(section)
            self.setup.setup([section])
        for item in NAMES:
            item = getattr(config, item)
            self.assertTrue(self.setup.api.exists(item))

if __name__ == '__main__':
    unittest.main()
