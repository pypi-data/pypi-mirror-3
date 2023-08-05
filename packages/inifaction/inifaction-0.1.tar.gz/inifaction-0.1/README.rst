.. _Webfaction: http://webfaction.com 
.. _API: http://docs.webfaction.com/xmlrpc-api/apiref.html


Overview
========

``inifaction`` makes possible to write an INI style file and setup a Webfaction_ project with it through Webfaction's API_.

It has a command line utility but it's possible to also use the API implementation of ``inifaction`` as a module.


Command line utility
====================

Create a template to configure a project::

    inifaction template -f config.ini

After making the needed changes, call the API of Webfaction and setup the project::

    inifaction setup -f config.ini

If any error happens, it will continue with the setup. Later on, you can setup only the section where the error happened::

    inifaction setup -f config.ini -s domains


As a module
===========

The API is created instantiating `inifaction.api.API` with the URL as parameter. Login requires user, password and the machine::

    # Setup the API
    from inifaction import API_URL
    from inifaction.api import API

    api = API(API_URL)
    api.login('user', 'password', 'Web210')

All the configuration sections of Webfacion's API are available at `inifaction.items` as items. Those items hold all the needed information to call the API with certain parameters, depending on the API's call. 

For example, we can create an email address::

    from inifaction.items import Email

    email = Email('example@email.net', ['example_target_mailbox', 'target@emai.net'],
                autoresponder_on=True, autoresponder_subject='Hi!', autoresponder_message='Hello!',
                autoresponder_from='dont-answer@email.net', script_machine='', script_path='')

Calling the item's ``args`` function with the API call type (``create``, ``update`` or ``delete``), returns the needed parameters to making that call. This happens automatically on API's level::

    # Create the email
    api.create(email)

    # Change the item and update it
    email = email._replace(email_address='other@emai.net')
    api.update(email)

    # Check if it exists
    api.exists(email)

    # List all the emails
    api.list('emails')

    # Delete the email
    api.delete(email)

    # Delete all the emails
    api.delete_all('emails')

It's possible to subclass the default items and create customized ones, it only requires to change `inifaction.SECTIONS` and `inifaction.NAMES` values to point to the customized item. 
