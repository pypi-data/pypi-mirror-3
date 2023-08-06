# coding: utf-8

import cyclone.escape
import cyclone.redis
import cyclone.sqlite
import cyclone.web

from twisted.enterprise import adbapi


class BaseHandler(cyclone.web.RequestHandler):
    #def get_current_user(self):
    #    user_json = self.get_secure_cookie("user")
    #    if user_json:
    #        return cyclone.escape.json_decode(user_json)

    def get_user_locale(self):
        lang = self.get_secure_cookie("lang")
        if lang:
            return cyclone.locale.get(lang)


class DatabaseMixin(object):
    mysql = None
    redis = None
    sqlite = None

    @classmethod
    def setup(self, settings):
        conf = settings.get("mysql_settings")
        if conf:
            DatabaseMixin.mysql = adbapi.ConnectionPool("MySQLdb",
                            host=conf.host, port=conf.port, db=conf.database,
                            user=conf.username, passwd=conf.password,
                            cp_min=1, cp_max=conf.poolsize,
                            cp_reconnect=True, cp_noisy=conf.debug)

        conf = settings.get("redis_settings")
        if conf:
            DatabaseMixin.redis = cyclone.redis.lazyConnectionPool(
                            conf.host, conf.port, conf.dbid, conf.poolsize)

        conf = settings.get("sqlite_settings")
        if conf:
            DatabaseMixin.sqlite = cyclone.sqlite.InlineSQLite(conf.database)
