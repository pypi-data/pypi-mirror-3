#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import functools
import sys

import cyclone.redis
import cyclone.web

from twisted.python import log
from twisted.internet import defer, reactor

class Application(cyclone.web.Application):
    def __init__(self):
        # Defaults to localhost:6379, dbid=0
        redisdb = cyclone.redis.lazyRedisConnectionPool()

        handlers = [
            (r"/", IndexHandler, dict(redisdb=redisdb)),
        ]
        cyclone.web.Application.__init__(self, handlers, debug=True)


def HTTPBasic(method):
    @defer.inlineCallbacks
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            auth_type, auth_data = self.request.headers["Authorization"].split()
            assert auth_type == "Basic"
            usr, pwd = base64.b64decode(auth_data).split(":", 1)
        except:
            raise cyclone.web.HTTPAuthenticationRequired

        try:
            redis_pwd = yield self.redisdb.get("cyclone:%s" % usr)
        except Exception, e:
            log.msg("Redis failed to get('cyclone:%s'): %s" % (usr, str(e)))
            raise cyclone.web.HTTPError(503) # Service Unavailable

        if pwd != str(redis_pwd):
            raise cyclone.web.HTTPAuthenticationRequired
        else:
            self._current_user = usr
            defer.returnValue(method(self, *args, **kwargs))
    return wrapper


class IndexHandler(cyclone.web.RequestHandler):
    def initialize(self, redisdb):
        self.redisdb = redisdb

    @HTTPBasic
    def get(self):
        self.write("Hi, %s." % self._current_user)


def main():
    log.startLogging(sys.stdout)
    log.msg(">>>> Set the password from command line: redis-cli set cyclone:root 123")
    log.msg(">>>> Then authenticate as root/123 from the browser")
    reactor.listenTCP(8888, Application(), interface="127.0.0.1")
    reactor.run()


if __name__ == "__main__":
    main()
