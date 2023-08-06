
Introduction
============

``collective.recipe.bluebream`` is a ``zc.buildout`` recipe you can use to bootstrap a `Bluebream`_ project. It does the following:

- Requires the packages required by BlueBream (according to the sample project setup described here: http://bluebream.zope.org/doc/1.0/gettingstarted.html)
- Installs ``bin/paster``
- Installs a small WSGI application
- Installs ZCML configuration files
- Adds some var directories if they do not exist
- Supports develop eggs

Installation
============

Create a buildout::

    $ virtualenv-2.7 .
    $ bin/pip install zc.buildout
    $ bin/buildout init

Then edit buildout.cfg; use ``collective.recipe.bluebream`` like any recipe: just add a part and configure the ``recipe`` parameter. You should also configure a known good set of packages via the extends parameter::

    [buildout]
    extends = http://download.zope.org/bluebream/bluebream-1.0.cfg
    parts =
        bluebream
    versions = versions

    [bluebream]
    recipe = collective.recipe.bluebream

Then run buildout::

    $ bin/buildout

Develop eggs
------------

As of version **0.3.0**, ``collective.recipe.bluebream`` supports package development via the ``eggs`` parameter::

    [buildout]
    develop =
        src/my.package

    [bluebream]
    eggs =
        my.package

Configuration
=============

You should now have a ``bin/paster`` script. To run ``bluebream``, you will also need a WSGI configuration file and a Zope configuration file. Here are some sample configuration files to get you started.

bluebream.ini
-------------

Cut/paste, save as bluebream.ini::

    [loggers]
    keys = root, wsgi

    [handlers]
    keys = console, accesslog

    [formatters]
    keys = generic, accesslog

    [formatter_generic]
    format = %(asctime)s %(levelname)s [%(name)s] %(message)s

    [formatter_accesslog]
    format = %(message)s

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = ERROR
    formatter = generic

    [handler_accesslog]
    class = FileHandler
    args = ('access.log', 'a')
    level = INFO
    formatter = accesslog

    [logger_root]
    level = INFO
    handlers = console

    [logger_wsgi]
    level = INFO
    handlers = accesslog
    qualname = wsgi
    propagate = 0

    [filter:translogger]
    use = egg:Paste#translogger
    setup_console_handler = False
    logger_name = wsgi

    [filter-app:main]
    # Change the last part from 'ajax' to 'pdb' for a post-mortem debugger
    # on the console:
    use = egg:z3c.evalexception#ajax
    next = zope

    [app:zope]
    use = egg:collective.recipe.bluebream
    filter-with = translogger

    [server:main]
    use = egg:Paste#http
    host = 127.0.0.1
    port = 8080

    [DEFAULT]
    # set the name of the zope.conf file
    zope_conf = %(here)s/zope.conf

zope.conf
---------

Cut/paste, save as zope.conf::

    # main zope configuration file for debug mode

    # Identify the component configuration used to define the site:
    site-definition bluebream.zcml

    <zodb>

      <filestorage>
        path var/filestorage/Data.fs
        blob-dir var/blobstorage
      </filestorage>

    # Uncomment this if you want to connect to a ZEO server instead:
    #  <zeoclient>
    #    server localhost:8100
    #    storage 1
    #    # ZEO client cache, in bytes
    #    cache-size 20MB
    #    # Uncomment to have a persistent disk cache
    #    #client zeo1
    #  </zeoclient>
    </zodb>

    <eventlog>
      # This sets up logging to both a file and to standard output (STDOUT).
      # The "path" setting can be a relative or absolute filesystem path or
      # the tokens STDOUT or STDERR.

      <logfile>
        path z3.log
        formatter zope.exceptions.log.Formatter
      </logfile>

      <logfile>
        path STDOUT
        formatter zope.exceptions.log.Formatter
      </logfile>
    </eventlog>

    #developer mode
    devmode on

Execution
=========

Now you can run paster::

    $ bin/paster serve bluebream.ini

And open ``http://localhost:8080`` in your browser.

Completion
==========

That's it! Checkout http://bluebream.zope.org for more information about Bluebream.

.. _`Bluebream`: http://bluebream.zope.org

