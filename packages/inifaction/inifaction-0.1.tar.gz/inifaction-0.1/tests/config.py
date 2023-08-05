from inifaction.items import (Email, Mailbox, Domain, Website, App, DnsOverride,
        Database)

login = ('apitesting', 'f882fc1c', 'Web304')
email = Email(
        email_address='example@email.net', 
        targets=['target@email.net', 'example_mailbox'],
        autoresponder_on=True,
        autoresponder_subject='This is a test',
        autoresponder_message='Hi! This is a test case',
        autoresponder_from='test@email.net',
        script_machine='Web304',
        script_path='/home/apitesting/script.sh',
        )

mailbox = Mailbox(
        mailbox='example_mailbox',
        enable_spam_protection=True,
        discard_spam=True,
        spam_redirect_folder='spam',
        use_manual_procmailrc=True,
        manual_procmailrc='procmailrc',
        )
mailbox.password = 'some_p@ss'

domain = Domain(
        domain='email.net',
        subdomains=['www', 'ftp'],
        )

website = Website(
        name='example',
        subdomains=['email.net', 'www.email.net'],
        ip='',
        https=True,
        apps=[('example_app', '/')],
        )

app = App(
        name='example_app',
        type='django131_mw33_27',
        extra_info='',
        autostart=False,
        script_code='',
        )

db = Database(
        name='apitesting_database',
        db_type='postgresql',
        password='thepass',
        )

dns_override = DnsOverride(
        domain='email.net',
        a_ip='66.66.66.66',
        cname='',
        mx_name='',
        mx_priority='',
        spf_record='',
        )
