#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
http.app
~~~~~~~~~

Core of HTTP Request & Response service

:copyright: (c) 2011 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/httpecho
"""

import os
import sys
import time
import tornado.ioloop
import tornado

try:
    import urlparse
except ImportError:
    # Python3
    from urllib import parse as urlparse

try:
    from urlparse import parse_qs
    parse_qs # placate pyflakes
except ImportError:
    try:
        # Python3
        from urllib.parse import parse_qs
    except ImportError:
        # fall back for Python 2.5
        from cgi import parse_qs

from tornado.web import Application
from tornado.options import define, options
from tornado import httpserver
from tornado import autoreload
from tornado.escape import utf8
import logging as logging_module
from tornado.options import _LogFormatter
from logging import StreamHandler


define("port", default=8889, help="run HTTP on the given port", type=int)
define("ssl_port", default=8890, help="run HTTPS on the given port", type=int)

logger = logging_module.getLogger('httpecho')

def configure_logging(logging):
    """Configure logging handler"""
    if logging.upper() not in ['DEBUG', 'INFO', 'CRITICAL',
                               'WARNING', 'ERROR']:
        return

    logger.setLevel(getattr(logging_module, logging.upper()))

    if not logger.handlers:
        channel = StreamHandler()
        channel.setFormatter(_LogFormatter(color=False))
        logger.addHandler(channel)
    logger.info("Logging handler configured with level {0}".format(logging))


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
from pprint import pprint

def rel(*args):
    return os.path.join(PROJECT_ROOT, *args)



class HTTPApplication(Application):
    """Base application
    """

    def __init__(self):
        self.dirty_handlers = [
            (r"/(?P<path>.*)", MainHandler),
            ]

        settings = dict(
            site_title="HTTP echo & debug",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret="11oETzfjkrebfgjKXQLKHFJKkjjnFLDnDKJjNSDAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            autoescape=None,
        )
        tornado.web.Application.__init__(self, [(h[0], h[1]) for h in self.dirty_handlers], **settings)


class CustomHandler(tornado.web.RequestHandler):
    """Custom handler with good methods
    """

    def __init__(self, *args, **kwargs):
        super(CustomHandler, self).__init__(*args, **kwargs)
        self.set_header("Server", "LightBeer/0.568")

    def json_response(self, data, finish=True):
        output_json = utf8(tornado.escape.json_encode(data))
        # self.set_header("Content-Type", "application/json")
        if finish is True:
            self.finish(output_json)
        else:
            return output_json

    def get_data(self):
        data = {}
        data['args'] = dict([(k, v) for k, v in self.request.arguments.items()])
        data['headers'] = dict([(k, v) for k, v in self.request.headers.items()])
        data['ip'] = self.request.headers.get(
            "X-Real-Ip", self.request.headers.get(
                "X-RealI-IP",
                self.request.headers.get("X-Forwarded-For", self.request.remote_ip)))
        data['url'] = self.request.full_url()
        data['request_time'] = self.request.request_time()
        data['start_time'] = self.request._start_time

        if self.request.method in ("POST", "PUT", "PATCH"):
            data['body'] = self.request.body
            data['files'] = {}
            for k, v in self.request.files.items():
                data['files'][k] = [dict(filename=x['filename'],
                                         content_type=x['content_type'],
                                         body=x['body'] if len(x['body']) < 500 else x['body'][:500])
                                    for x in v]
        logger.debug(data)
        logger.debug(self.request)
        return data



class MainHandler(CustomHandler):
    """GET method
    """

    def get(self, *args, **kwargs):
        self.json_response(self.get_data())


    def post(self,*args,**kwargs):
        return self.json_response(self.get_data())

    def put(self,*args,**kwargs):
        return self.json_response(self.get_data())

    def delete(self,*args,**kwargs):
        return self.json_response(self.get_data())


application = HTTPApplication()

def main():
    tornado.options.parse_command_line()
    configure_logging('debug')
    http_server = httpserver.HTTPServer(application)

    certfile = rel("server.crt")
    keyfile = rel("server.key")

    if os.path.exists(certfile) and os.path.exists(keyfile):
        https_server = httpserver.HTTPServer(application, ssl_options={
            "certfile": certfile,
            "keyfile": keyfile})
        https_server.listen(options.ssl_port)

    http_server.listen(options.port)
    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(io_loop=ioloop, check_time=100)
    logger.debug("starting server {0}".format(options.port))
    ioloop.start()



if __name__ == "__main__":
    main()
