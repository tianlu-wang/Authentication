__author__ = 'TianluWang'
# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import auth.sign_up
import auth.log_in
import auth.reset_request
import logging
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='auth.log',
                    filemode='w')

if __name__ == "__main__":

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/sign_up', auth.sign_up.SignUpHandler), (r'/log_in', auth.log_in.LogInHangdler),
                  (r'/reset_request', auth.reset_request.ResetRequestHandler)],
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()