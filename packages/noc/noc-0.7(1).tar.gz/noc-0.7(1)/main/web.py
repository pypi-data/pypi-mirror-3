# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-web daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import os
import errno
import signal
## Django modules
import django.core.handlers.wsgi
## Third-party modules
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver
from tornado.process import cpu_count
## NOC modules
from noc.lib.daemon import Daemon


class AppStaticFileHandler(tornado.web.StaticFileHandler):
    """
    Serve applications' static files.
    Rewrite urls from
    /<module>/<app>/(js|img|css)/file
    to
    <module>/apps/<app>/(js|img|css)/file
    """
    def get(self, path, include_body=True):
        p = path.split("/")
        path = "/".join([p[1], "apps"] + p[2:])
        return super(AppStaticFileHandler, self).get(path, include_body)


class Web(Daemon):
    """
    noc-web daemon
    """
    daemon_name = "noc-web"

    def setup_opt_parser(self):
        """
        Add --listen option
        """
        self.opt_parser.add_option("-l", "--listen", action="store",
                                   dest="listen", default="",
                                   help="listen at address:port")

    def run(self):
        if self.options.listen:
            listen = self.options.listen
        else:
            listen = self.config.get("web", "listen")
        if ":" in listen:
            address, port = listen.split(":")
        else:
            address, port = "127.0.0.1", listen
        port = int(port)

        noc_wsgi = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler()
        )

        application = tornado.web.Application([
            # /static/
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {
                "path": "static"}),
            # /media/
            (r"^/media/(.*)", tornado.web.StaticFileHandler, {
                "path": "contrib/lib/django/contrib/admin/media"}),
            # /doc/
            (r"^/doc/(.*)", tornado.web.StaticFileHandler, {
                "path": "share/doc/users_guide/html"}),
            # NOC application's js, img and css files
            # @todo: write proper static handler
            (r"(/[^/]+/[^/]+/(?:js|img|css)/.+)", AppStaticFileHandler, {
                "path": self.prefix}),
            # / -> /main/desktop/
            (r"^/$", tornado.web.RedirectHandler, {"url": "/main/desktop/"}),
            # Pass to NOC
            (r"^.*$", tornado.web.FallbackHandler, {"fallback": noc_wsgi})
        ])
        logging.info("Loading site")
        logging.info("Listening %s:%s" % (address, port))
        # Create tornado server
        self.server = tornado.httpserver.HTTPServer(application)
        self.server.bind(port, address)
        # Run children
        nc = self.config.getint("web", "workers")
        if nc == 0:
            nc = cpu_count()
        self.t_children = set()
        while True:
            # Run children
            while len(self.t_children) < nc:
                pid = os.fork()
                if pid == 0:
                    self.children_loop()
                else:
                    logging.info("Running child %d" % pid)
                    self.t_children.add(pid)
            # Wait for status
            try:
                pid, status = os.wait()
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                raise
            if pid not in self.t_children:
                continue
            self.t_children.remove(pid)
            logging.info("Exiting child %d" % pid)

    def children_loop(self):
        self.t_children = None
        # Initialize pending sockets
        sockets = self.server._pending_sockets
        self.server._pending_sockets = []
        self.server.add_sockets(sockets)
        # Connect to mongodb
        import noc.lib.nosql
        # Initialize site
        from noc.lib.app import site
        site.autodiscover()
        # Run children's I/O loop
        tornado.ioloop.IOLoop.instance().start()

    def SIGTERM(self, signo, frame):
        if self.t_children:
            for pid in self.t_children:
                logging.info("Stopping child %d" % pid)
                os.kill(pid, signal.SIGTERM)
        os._exit(0)
