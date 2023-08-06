# -*- coding: utf-8 -*- 

import os, sys
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from django.conf import settings as _settings


PORT = 8080


import tornado.web
from django.db import close_connection
from django.core import signals


class DjangoHandler(tornado.web.FallbackHandler):
    """A RequestHandler that wraps another HTTP server callback.

    The fallback is a callable object that accepts an HTTPRequest,
    such as an Application or tornado.wsgi.WSGIContainer.  This is most
    useful to use both tornado RequestHandlers and WSGI in the same server.
    Typical usage::

        wsgi_app = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler())
        application = tornado.web.Application([
            (r"/foo", FooHandler),
            (r".*", FallbackHandler, dict(fallback=wsgi_app),
        ])
    """
    def initialize(self, fallback):
        self.fallback = fallback
        signals.request_finished.disconnect(close_connection())



class Command(BaseCommand):

    def tornado_old(self, *args, **options):

        import tornado.httpserver
        import tornado.ioloop
        import tornado.wsgi

        import django.core.handlers.wsgi

        print 'Collect static'
        call_command('collectstatic', interactive=False)

        application = django.core.handlers.wsgi.WSGIHandler()
        container = tornado.wsgi.WSGIContainer(application)


        static_path = __file__[:__file__.rfind('enre/serve/management/commands/serve.py') - 1]
        static_path = os.path.join(static_path, 'static')
        print static_path

        app1 = tornado.web.Application([
            (r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(static_path, 'enre/erp/core/static'))),
        ])

        tornado_app = tornado.web.Application(
            [
                #('/hello-tornado', HelloHandler),
                #(r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(static_path, 'enre/erp/core/static'))),
                (r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=static_path)),
                ('.*', tornado.web.FallbackHandler, dict(fallback=container)),
            ]
        )


        #sockets = tornado.netutil.bind_sockets(PORT)
        #tornado.process.fork_processes(10)
        http_server = tornado.httpserver.HTTPServer(tornado_app)
        #http_server.add_sockets(sockets)
        http_server.listen(PORT)
        tornado.ioloop.IOLoop.instance().start()

        print 'Serve !!!!'
        pass



    def tornado(self, *args, **options):

        import tornado.httpserver
        import tornado.ioloop
        import tornado.wsgi
        import django.core.handlers.wsgi
        import tornado.process
        import tornado.netutil

        call_command('collectstatic', interactive=False)

        application = django.core.handlers.wsgi.WSGIHandler()
        container = tornado.wsgi.WSGIContainer(application)

        static_path = __file__[:__file__.rfind('enre/serve/management/commands/serve.py') - 1]
        static_path = os.path.join(static_path, 'static')


        tornado_app = tornado.web.Application(
            [
                #('/hello-tornado', HelloHandler),
                #(r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(static_path, 'enre/erp/core/static'))),
                (r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=static_path)),
                ('.*', DjangoHandler, dict(fallback=container)),
                ]
        )


        sockets = tornado.netutil.bind_sockets(PORT)
        tornado.process.fork_processes(10)
        http_server = tornado.httpserver.HTTPServer(tornado_app)
        http_server.add_sockets(sockets)
        #http_server.listen(PORT)
        tornado.ioloop.IOLoop.instance().start()



    def cherrypy(self, *args, **options):
        import cherrypy
        from django.core.wsgi import WSGIHandler
        from django.conf import settings

        call_command('collectstatic', interactive=False)
        static_path = __file__[:__file__.rfind('enre/serve/management/commands/serve.py') - 1]
        static_path = os.path.join(static_path, 'static')
        print 'Static Path: ', static_path

        cherrypy.tree.graft(WSGIHandler())

        static_handler = cherrypy.tools.staticdir.handler(section="/", dir='static',
            root='/Users/gratromv/Projects/enre/enre/')

        cherrypy.tree.mount(static_handler, settings.STATIC_URL)
        cherrypy._cpconfig.Config({
            'server.socket_host': '0.0.0.0',
            'server.thread_pool': 20,
            'tools.encode.encoding': 'utf-8'
        })

        cherrypy.engine.start()
        cherrypy.engine.block()

        pass

    def handle(self, *args, **options):
        self.tornado()
