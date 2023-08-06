=======
cyclone
=======
:Info: See `github <http://github.com/fiorix/cyclone>`_ for the latest source.
:Author: Alexandre Fiori <fiorix@gmail.com>

About
=====

cyclone is a low-level network toolkit, which provides support for HTTP 1.1 in an API very similar to the one implemented by the `Tornado <http://tornadoweb.org>`_ web server - which was developed by `FriendFeed <http://friendfeed.com>`_ and later released as open source / free software by `Facebook <http://facebook.com>`_.

Key differences between cyclone and tornado
-------------------------------------------

- cyclone is `Twisted <http://twistedmatrix.com>`_ protocol, therefore it may be used in conjunction with any other protocol implemented in Twisted.
- Localization is based on the standard `Gettext <http://www.gnu.org/software/gettext/>`_ instead of the CSV implementation in the original tornado. The gettext support has been merged back into tornado.
- It ships with an asynchronous HTTP client based on `TwistedWeb <http://twistedmatrix.com/trac/wiki/TwistedWeb>`_. It's not compatible with with one provided by tornado - which is based on `PyCurl <http://pycurl.sourceforge.net/>`_. (The HTTP server code is NOT based on TwistedWeb, for several reasons)
- Native support for XMLRPC and JsonRPC. (see the `rpc demo <http://github.com/fiorix/cyclone/tree/master/demos/rpc/>`_)
- WebSocket protocol class is just like any other Twisted Protocol (i.e.: LineReceiver; see the `websocket demo <http://github.com/fiorix/cyclone/tree/master/demos/websocket/>`_)
- Support for sending e-mail based on `Twisted Mail <http://twistedmatrix.com/trac/wiki/TwistedMail>`_, with authentication and TLS, plus an easy way to create plain text or HTML messages, and attachments. (see the `e-mail demo <http://github.com/fiorix/cyclone/tree/master/demos/email>`_)
- Built-in support for `Redis <http://code.google.com/p/redis/>`_, based on `txredisapi <http://github.com/fiorix/txredisapi>`_. We usually need an in-memory caching server like memcache for web applications. However, we prefer redis over memcache because it supports more operations like pubsub, various data types like sets, hashes (python dict), and persistent storage. See the `redis demo <http://github.com/fiorix/cyclone/tree/master/demos/redis/>`_ for details.
- Support for HTTP Authentication. See the `authentication demo <http://github.com/fiorix/cyclone/tree/master/demos/httpauth/>`_ for details.
- Support for Bottle-like API, Twistd application and Twistd plugin.

Advantages of being a Twisted Protocol
--------------------------------------

- Easy deployment of applications, using `twistd <http://twistedmatrix.com/documents/current/core/howto/basics.html>`_.
- RDBM support via: `twisted.enterprise.adbapi <http://twistedmatrix.com/documents/current/core/howto/rdbms.html>`_.
- NoSQL support for MongoDB (`TxMongo <http://github.com/fiorix/mongo-async-python-driver>`_) and Redis (`TxRedisAPI <http://github.com/fiorix/txredisapi>`_).
- May combine many more functionality within the webserver: sending emails, communicating with message brokers, etc...

Benchmarks
----------

Check out the `benchmarks <http://wiki.github.com/fiorix/cyclone/benchmarks>`_ page.

Tips and Tricks
===============

As a clone, the API implemented in cyclone is almost the same of Tornado. Therefore you may use the `Tornado Documentation <http://www.tornadoweb.org/documentation>`_ for stuff like templates and so on.

The snippets below will show some tips and tricks regarding the few differences between the two.

Hello World
-----------

::

    #!/usr/bin/env python
    # coding: utf-8

    import cyclone.web
    import sys
    from twisted.internet import reactor
    from twisted.python import log

    class MainHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    def main():
        log.startLogging(sys.stdout)
        application = cyclone.web.Application([
            (r"/", MainHandler)
        ])

        reactor.listenTCP(8888, application, interface="127.0.0.1")
        reactor.run()

    if __name__ == "__main__":
        main()


Twisted Application and Plugin
------------------------------

The advantage of being a Twisted Application is that you don't need to care about basic daemon features like forking, creating pid files, changing application's user and group permissions, and selecting the proper reactor within the code.

Instead, the application may be run by ``twistd``, as follows::

    for testing:
    /usr/bin/twistd --nodaemon --python=foobar.tac

    for production:
    /usr/bin/twistd --pidfile=/var/run/foobar.pid \
                    --logfile=/var/log/foobar.log \
                    --uid=nobody --gid=nobody \
                    --reactor=epoll \
                    --python=foobar.tac

Following is the *Hello World* as a twisted application::

    # coding: utf-8
    # twisted application: foobar.tac

    import cyclone.web
    from twisted.application import service, internet

    class IndexHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("hello world")

    foobar = cyclone.web.Application([(r"/", IndexHandler)])

    application = service.Application("foobar")
    internet.TCPServer(8888, foobar(),
        interface="127.0.0.1").setServiceParent(application)

Twisted Plugin is the recommended way to go for production. Create new projects
right away off of the generic application skeleton shipped with cyclone::

    python -m cyclone.app --help

Check out the README.rst within the new project and have fun.

Localization
------------

The ``cyclone.locale`` provides an API based on the Python ``gettext`` module.

Because of that, there is *one* extra option that may be passed to ``cyclone.locale.load_gettext_translations(path, domain="cyclone")``, which the is the gettext's domain. The default domain is *cyclone*.

Following is a step-by-step guide to implement localization in any cyclone application:

1. Create a python script or twisted application with translatable strings::

    # coding: utf-8
    # twisted application: foobar.tac

    import cyclone.web
    import cyclone.locale
    from twisted.application import service, internet

    class BaseHandler(cyclone.web.RequestHandler):
        def get_user_locale(self):
            lang = self.get_cookie("lang")
            return cyclone.locale.get(lang)

    class IndexHandler(BaseHandler):
        def get(self):
            self.render("index.html")

        def post(self):
            _ = self.locale.translate
            name = self.get_argument("name")
            self.write(_("the name is: %s" % name))

    class LangHandler(cyclone.web.RequestHandler):
        def get(self, lang):
            if lang in cyclone.locale.get_supported_locales():
                self.set_cookie("lang", lang)
            self.redirect("/")

    class Application(cyclone.web.Application):
        def __init__(self):
            handlers = [
                (r"/", IndexHandler),
                (r"/lang/(.+)", LangHandler),
            ]

            settings = {
                "static_path": "./static",
                "template_path": "./template",
            }

            cyclone.locale.load_gettext_translations("./locale", "foobar")
            cyclone.web.Application.__init__(self, handlers, **settings)

    application = service.Application("foobar")
    internet.TCPServer(8888, Application(),
        interface="127.0.0.1").setServiceParent(application)

2. Create a file in ``./template/index.html`` with translatable strings::

    <html>
    <body>
        <form action="/" method="post">
        <p>{{ _("write someone's name:") }}</p>
        <input type="text" name="name">
        <input type="submit" value="{{ _('send') }}">
        </form>

        <br>
        <p>{{ _("change language:") }}</p>
        <p><a href="/lang/en_US">English (US)</a></p>
        <p><a href="/lang/pt_BR">Portuguese (BR)</a></p>
    </body>
    </html>

3. Generate PO translatable file from the source code, using ``xgettext``:

    You will notice that ``xgettext`` cannot parse HTML properly. It was
    first designed to parse C files, and now it supports many other
    languages including Python.

    In order to parse lines like ``<input type="submit" value="{{ _('send') }}">``,
    you'll need an extra script to pre-process the files.

    Here's what you can use as ``fix.py``::

        #!/usr/bin/env python
        # coding: utf-8
        # fix.py

        import re, sys

        if __name__ == "__main__":
            try:
                filename = sys.argv[1]
                assert filename != "-"
                fd = open(filename)
            except:
                fd = sys.stdin

            line_re = re.compile(r"""['"]{{|}}['"] """)
            for line in fd:
                line = line_re.sub(r"", line)
                sys.stdout.write(line)
            fd.close()

    Then, call ``xgettext`` to generate the PO translatable file::

        cat foobar.tac template/index.html | python fix.py | \
            xgettext --language=Python --from-code=utf-8 --keyword=_:1,2 -d foobar

    This will create a file named ``foobar.po``, which needs to be
    translated, then compiled into an MO file::

        vi foobar.po
        (translate everything, :wq)

        mkdir -p ./locale/pt_BR/LC_MESSAGES/
        msgfmt foobar.po -o ./locale/pt_BR/LC_MESSAGES/foobar.mo

4. Finally, test the internationalized application::

    twistd -ny foobar.tac

There is also a complete example with pluralization in `demos/locale <http://github.com/fiorix/cyclone/tree/master/demos/locale>`_.

Authenticated and Asynchronous decorators
-----------------------------------------

Tornado provides decorator functions for asynchronous and authenticated
methods. Obviously, they're also implemented in cyclone, and yet more
powerful when combined with a famous Twisted decorator: ``defer.inlineCallbacks``.

The ``cyclone.web.authenticated`` decorator may be combined with ``defer.inlineCallbacks``,
however, there's a basic rule to use them together. Considering that the authenticated
decorator will check user credentials, and, depending on the result, it will
continue processing the request OR redirect the request to the login page,
it has to be used *before* the ``defer.inlineCallbacks`` to function properly::

    class IndexHandler(cyclone.web.RequestHandler):
        @cyclone.web.authenticated
        @defer.inlineCallbacks
        def get(self):
            result = yield something()
            self.write(result)

On the other hand, the ``cyclone.web.asynchronous`` decorator will keep the request open
until you explicitly call ``self.finish()`` later on. Of course, it may also be combined
with ``defer.inlineCallbacks``, but it MUST be placed *after* to function properly::

    class Indexhandler(cyclone.web.RequestHandler):
        @defer.inlineCallbacks
        @cyclone.web.asynchronous
        def get(self):
            result = yield something()
            self.finish(result)

Yes, you may combine the three decorators to have the most powerful and simple code
in cyclone, like this::

    class Indexhandler(cyclone.web.RequestHandler):
        @cyclone.web.authenticated
        @defer.inlineCallbacks
        @cyclone.web.asynchronous
        def get(self):
            try:
                result = yield self.redisdb.get("foo")
            except Exception, e:
                log.msg("Redis query failed: %s" % str(e))
                raise cyclone.web.HTTPError(503) # Service Unavailable

            if not result:
                raise cyclone.web.HTTPError(404)

            self.finish({"result":result})

More options and tricks
-----------------------

- Keep-Alive

    Because of the HTTP 1.1 support, sockets aren't always closed when you call
    ``self.finish()`` in a RequestHandler. cyclone lets you enforce that by setting
    the ``no_keep_alive`` attribute attribute in some of your RequestHandlers::

        class IndexHandler(cyclone.web.RequestHandler):
            no_keep_alive = True
            def get(self):
                ...

- Socket closed notification

    One of the great features of TwistedWeb is the ``request.notifyFinish()``,
    which is also available in cyclone.
    This method returns a deferred which is fired when the request socket
    is closed, by either ``self.finish()``, someone closing their browser
    while receiving data, or closing the connection of a Comet request::

        class IndexHandler(cyclone.web.RequestHandler):
            def get(self):
                ...
                d = self.notifyFinish()
                d.addCallback(remove_from_comet_handlers_list)

- HTTP X-Headers

    When running a cyclone-based application behind `Nginx <http://nginx.org/en/>`_, 
    it's very important to make it automatically use X-Real-Ip and X-Scheme HTTP
    headers. In order to make cyclone recognize those headers, the option ``xheaders=True``
    must be set in the Application settings::

        class Application(cyclone.web.Application):
            def __init__(self):
                handlers = [
                    (r"/", IndexHandler),
                ]

                settings = {
                    "xheaders": True
                    "static_path": "./static",
                }

                cyclone.web.Application.__init__(self, handlers, **settings)

- Cookie-Secret generation

    What I use to generate the "cookie_secrect" key used in cyclone.web.Application's
    settings is something pretty simple, like this::

        >>> import uuid, base64
        >>> base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        'FoQv5hgLTYCb9aKiBagpJJYtLJInWUcXilg3/vPkUnI='


FAQ
---

- Where are the request headers?

    They are part of the request, dude::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                # self.request.headers is a dict
                user_agent = self.request.headers.get("User-Agent")

- How do I access raw POST data?

    Both raw POST data and GET/DELETE un-parsed query string are available::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                raw = self.request.query

            def post(self):
                raw = self.request.body

- Where is the request information, like remote IP address, HTTP method, URI and version?

    Everything is available as request attributes::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                remote_ip = self.request.remote_ip
                method = self.request.method
                uri = self.request.uri
                version = self.request.version

- How do I set my own headers for the reply?

    Guess what, use self.set_header(name, value)::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                self.set_header("Content-Type", "application/json")
                self.finish(cyclone.escape.json_encode({"success":True}))

- What HTTP methods are supported in RequestHandler?

    Well, almost all of them. HEAD, GET, POST, DELETE, PUT and OPTIONS are supported.
    TRACE is disabled by default, because it may get you in trouble. CONNECT has nothing
    to do with web servers, it's for proxies.

    For more information on HTTP 1.1 methods, please refer to the `RFC 2612 Fielding, et al. <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_.
    For information regarding TRACE vulnerabilities, please check the following links:
    `What is HTTP TRACE? <http://www.cgisecurity.com/questions/httptrace.shtml>`_ and
    `Apache Week, security issues <http://www.apacheweek.com/issues/03-01-24#news>`_.

    Supporting different HTTP methods in the same RequestHandler is easy::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                pass

            def head(self):
                pass

            ...


Credits
=======
Thanks to (in no particular order):

- Nuswit Telephony API

  - Granting permission for this code to be published and sponsoring

- Gleicon Moraes

  - Testing and using it in the `RestMQ <http://github.com/gleicon/restmq>`_ web service

- Vanderson Mota

  - Patching setup.py and PyPi maintenance

- Andrew Badr

  - Fixing auth bugs and adding current Tornado's features

- Jon Oberheide

  - Syncing code with Tornado and security features/fixes

- `Silas Sewell <https://github.com/silas>`_

  - Syncing code and minor mail fix

- `Twitter Bootstrap <https://github.com/twitter/bootstrap>`_

  - For making our demo applications look good
