=====================
cyclone-based project
=====================
:Info: This is the source code of $project_name
:Author: $name <$email>

About
=====

This file has been created automatically by cyclone-tool for $project_name.
It contains the following files:

- ``$modname.conf``: configuration file for the web server
- ``twisted/plugins/${modname}_plugin.py``: twisted plugin for running the web server
- ``$modname/__init__.py``: information such as author and version of this package
- ``$modname/web.py``: map of url handlers and main class of the web server
- ``$modname/config.py``: configuration parser for ``$modname.conf``
- ``$modname/views.py``: code of url handlers for the web server
- ``scripts/debian-init.d``: generic debian start/stop init script
- ``scripts/localefix.py``: script to fix html text before running ``xgettext``
- ``scripts/cookie_secret.py``: script for generating new secret key for the web server

Running
-------

For development and testing::

    twistd -n $modname [--help]

For production::

    twistd --logfile=/var/log/$project.log --pidfile=/var/run/$project.pid $modname

Some systems require that this directory is in PYTHONPATH prior to using twistd
plugins. If that is the case, then make sure you set it like this::

    export PYTHONPATH=`pwd`


Convert this document to HTML
-----------------------------

Well, since this is a web server, it might be a good idea to convert this document
to HTML before getting into customization details.

Because not everybody has `DocUtils <http://docutils.sourceforge.net/>`_ installed,
I recommend using the ``rst2a`` web service API::

    curl -F "rst=@README.rst" http://api.rst2a.com/1.0/rst2/html > frontend/static/readme.html

And point your browser to ``http://localhost:8888/static/readme.html`` after this server
is running.

For more information on the API, please check `http://rst2a.com/api/ <http://rst2a.com/api/>`_.


Customization
=============

This section is dedicated to explaining how to customize your brand new package.


Databases
---------

cyclone provides built-in support for Redis and SQLite databases. Because cyclone
is based on Twisted, it also supports any RDBM supported by the
``twisted.enterprise.adbapi`` module, like MySQL or PostgreSQL.

The default configuration file ``$modname.conf`` is already configured for using
both MySQL and Redis. The code for loading all the database settings is in
``$modname/config.py``. Feel free to comment or even remove such code and
configuration entries. It shouldn't break the web server.


Internationalization
--------------------

cyclone uses the standard ``gettext`` library for dealing with string translation.
Make sure you have the ``gettext`` package installed. If you don't, you won't be
able to translate your software.

For installing the ``gettext`` package on Debian and Ubuntu systems, do the following::

    apt-get install gettext

For Mac OS X, I'd suggest using `HomeBrew <http://mxcl.github.com/homebrew>`_.
If you already use HomeBrew, do the following::

    brew install gettext
    brew link gettext

For generating translatable files for HTML and Python code of your software,
do the following::

    cat frontend/template/*.html $modname/*.py | python scripts/localefix.py | \
        xgettext - --language=Python --from-code=utf-8 --keyword=_:1,2 -d $modname

Then translate $modname.po, compile and copy to the appropriate locale directory::

    (pt_BR is used as example here)
    vi $modname.po
    mkdir -p frontend/locale/pt_BR/LC_MESSAGES/
    msgfmt $modname.po -o frontend/locale/pt_BR/LC_MESSAGES/$modname.mo

There are sample translations for both Spanish and Portuguese in this package,
already compiled.


Cookie Secret
-------------

The current cookie secret key in ``$modname.conf`` was created during the
creation of this package. However, if you need a new one, you may run the
``scripts/cookie_secret.py`` script to generate a random key.

Credits
=======

- `cyclone <http://github.com/fiorix/cyclone>`_ web server.
