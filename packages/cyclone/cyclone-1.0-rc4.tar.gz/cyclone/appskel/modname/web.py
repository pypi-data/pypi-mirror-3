# coding: utf-8

import cyclone.locale
import cyclone.web

from $modname import views
from $modname.utils import DatabaseMixin

class Application(cyclone.web.Application):
    def __init__(self, settings):
        handlers = [
            (r"/",              views.IndexHandler),
            (r"/lang/(.+)",     views.LangHandler),
            (r"/sample/mysql",  views.SampleMySQLHandler),
            (r"/sample/redis",  views.SampleRedisHandler),
            (r"/sample/sqlite", views.SampleSQLiteHandler),
        ]

        # Initialize locales
        locales = settings.get("locale_path")
        if locales:
            cyclone.locale.load_gettext_translations(locales, "$modname")

        # Set up database connections
        DatabaseMixin.setup(settings)

        #settings["login_url"] = "/auth/login"
        cyclone.web.Application.__init__(self, handlers, **settings)
