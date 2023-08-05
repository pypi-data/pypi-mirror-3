==========
Nano tools
==========

This is a set of nano-size tools and apps for Django 1.3 and later.

Currently included:

activation
    A place to store activation-codes for e.g. authentication

badge
    User-badges worth certain points ala. StackOverflow

blog
    A very basic blog-app 

comments
    Unmoderated comments for logged-in users

chunk
    Templates stored in the database

faq
    Just about as simple a FAQ as is possible

privmsg
    Private messages with separate archives for sent an received

user
    A very basic user-registration- and password-handling app/tool

tools
    Utility-functions used by the above apps

Installation
------------

See INSTALL.txt for installation-instructions and TODO.txt for what's
missing.

Usage
-----

The apps and tools are in the namespace ``nano``.

Common for all apps
++++++++

Append ``nano.<subapp>`` to your INSTALLED_APPS, where ``subapp`` is any
of the tools listed above except ``tools``.

chunk
+++++
    Add 'nano.chunk.loader.Loader' to TEMPLATE_LOADERS.

user
++++
    Doesn't have any models so just hook up the views in an urls.py:

    - ``signup()``
    - ``password_change()``
    - ``password_reset()``

Settings for user
.................

NANO_USER_EMAIL_SENDER
    The From:-address on a password-reset email. If unset, no email is
    sent.

    **Default:** Not set

NANO_USER_TEST_USERS
    Special-cased usernames for live testing.

    **Default:** ``()``

NANO_USER_BLOG_TEMPLATE
    Template used for auto-blogging new users. 

    **Default:** ``blog/new_user.html``

Settings for all apps
---------------------

NANO_LOG_FORMAT
    Format for logs, see Python's ``logging``-module

    **Default:** ``'%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s %(message)s'``

NANO_LOG_FILE
    File to log to, see Python's ``logging``-module

    **Default:** ``'/tmp/nano.log'``


:Version: 0.4
