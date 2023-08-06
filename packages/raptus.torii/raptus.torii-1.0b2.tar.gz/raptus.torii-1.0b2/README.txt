Introduction
============
Torii allows access to a running zope server over a unix-domain-socket. Torii makes it
also possible to run scripts from the command line on the server. In addition it provides 
a python-prompt. That means full access to the Zope and ZODB at runtime.


Usage
=====
If you use the buildout-recipe, a shell-script is generated in buildout-directory/bin/torii.
When the zope server is started, execute ./bin/torii in an other shell.

Options:
--------

:help:            print help text and exit
                      
:debug:           interactive mode
                 
:list:            summary-list of all available scripts

:run <script>:    run the given script


Installation
============

The simplest way to install torii is to use raptus.recipe.torii in the buildout for your project.
This will add the required information in the zope.conf and build a startup script. The recipe provides
two buildout-variables. The first is named ${torii:additonal-conf} and holds the additional information
for the zope.conf. The second variable ${torii:eggs} is a list of all required eggs to add to the
python-path. Like this torii can also be used for non-plone projects.

Options
-------
socket-path
    path of the unix-domain-socket to create
threaded
    If true, torii creates a new thread for each connection.
    Default is False (which blocks requests when torii is active)
extends
    additional-packages for extending torii. e.g. raptus.troii.plone
params
    additional-parameters required for extending packages.
    notation: key:value;key:value or key:value'newline'key:value

Example
-------
::

    [buildout]
    parts =
        torii
        ...(other parts)...

    [torii]
    recipe = raptus.recipe.torii
    socket-path = ${buildout:directory}/var/torii.sock
    threaded = True
    extends =
        raptus.torii.plone
        raptus.torii.ipython
    params =
        plone-location:test.plone

    [instance]
    recipe = plone.recipe.zope2instance
    zope-conf-additional = ${torii:additional-conf}
    eggs =
        ...(other eggs)...
        ${buildout:eggs}
        ${torii:eggs}
        ...

    or

    [instance]
    recipe = plone.recipe.zope2instance
    zope-conf-additional = 
        <zodb_db myproject>
          mount-point /myproject
          <filestorage>
            path ${buildout:directory}/var/filestorage/myproject-prod.fs
            blob-dir ${buildout:directory}/var/blobstorage/prod
          </filestorage>
        </zodb_db>
        ${torii:additional-conf}
    eggs =
        ...(other eggs)...
        ${buildout:eggs}
        ${torii:eggs}
        ...


Additional components
=====================

raptus.torii.plone
    This additional package offers the interface to plone. It provides some scripts,
    a global variable 'plone' and sets the siteManager(access to persistence zope.components )
    at startup time.

raptus.torii.ipython
    An implementation of ipython. Code-completion, readline and colored python prompt.


Create new additional components
================================

Torii is pluggable. If you write a package, use the following attributes. These attributes 
are stored in your module (__init__.py) and by each connection they are read by torii.

utilities = dict(name=method)
    utilities are a set of helper functions. They will appear as globals
    in your python prompt. The globals can be extended with additional
    packages. To extend take a look in raptus.torii.plone.

properties = dict(name=method)
    properties are a set of helper attributes. Similar to the utilities, but
    properties are called by each connection. The call of the function is performed
    in the context of the connection. This means you can use local attributes
    in your function, like app, arguments ... Only the return value is stored 
    in the globals. To extend, take a look in raptus.torii.plone.

scripts = dict(name=path)
    scripts can be run directly without the python prompt over torii. It's
    easy to build you own scripts. Again please take a look
    at raptus.torii.plone

interpreter = Python
    The standard python interpreter. To create your own interpreter, subclass
    interpreter.AbstractInterpreter and override all methods. Take a look at
    raptus.torii.python and raptus.torii.ipython.ipython


Examples
========

Change the front-page text on the plonesite::

    # ./bin/torii debug
    Available global variables:
    conversation
    ls
    app
    sdir
    plone
    arguments
    
    In [1]: frontpage = plone['front-page']
    
    In [2]: frontpage.setText('The power of torii')
    
    In [3]: import transaction
    
    In [4]: transaction.commit()

Get all plone users::
    
    In [5]: plone.acl_users.getUsers()
    Out[5]: [<PloneUser 'dagobert_duck'>, <PloneUser 'donald_duck'>]


Tests
=====
Currently, there are no automated tests (yet). This project was created on SnowLeopard
and was running on plone 3 and plone 4.


Copyright and credits
=====================

raptus.torii is copyright 2010 by raptus_ , and is licensed under the GPL. 
See LICENSE.txt for details.

.. _raptus: http://www.raptus.com/ 


