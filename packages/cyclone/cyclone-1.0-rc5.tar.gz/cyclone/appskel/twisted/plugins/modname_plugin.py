# coding: utf-8

import $modname.config
import $modname.web

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import service, internet
from zope.interface import implements

class Options(usage.Options):
    optParameters = [
        ["port", "p", 8888, "TCP port to listen on", int],
        ["listen", "l", "127.0.0.1", "Network interface to listen on"],
        ["config", "c", "$modname.conf", "Configuration file with server settings"],
    ]

class ServiceMaker(object):
    implements(service.IServiceMaker, IPlugin)
    tapname = "$modname"
    description = "cyclone-based web server"
    options = Options

    def makeService(self, options):
        port = options["port"]
        interface = options["listen"]
        settings = $modname.config.parse_config(options["config"])
        return internet.TCPServer(port, $modname.web.Application(settings),
                                  interface=interface)

serviceMaker = ServiceMaker()
