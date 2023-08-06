MailSnake
=========

``MailSnake`` is a Python wrapper for `MailChimp API 1.3 <http://www.mailchimp.com/api/1.3/>`_

Installation
------------
::

    pip install mailsnake

Usage
-----

Basic Ping
~~~~~~~~~~

::

    from mailsnake import MailSnake
    from mailsnake.exceptions import *
    
    ms = MailSnake('YOUR MAILCHIMP API KEY')
    try:
        ms.ping() # returns "Everything's Chimpy!"
    except MailSnakeException:
        print 'An error occurred. :('

Catching Errors
~~~~~~~~~~~~~~~

::

    ms = MailSnake( 'my_wrong_mailchimp_api_key_that_does_not_exist')
    try:
        ms.ping() # returns "Everything's Chimpy!"
    except InvalidApiKeyException:
        print 'You have a bad API key, sorry.'

Note
----

API parameters must be passed by name. For example:

::

    ms.listMemberInfo(id='YOUR LIST ID', email_address='name@email.com')
