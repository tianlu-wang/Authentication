__author__ = 'TianluWang'

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import datetime
import logging
import traceback
import re
from auth.token import Encryption
from auth.config import errors


class ResetRequestHandler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error'}

        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(response)
            logging.error(traceback.format_exc())
            return
        email = payload['param']['email']
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            response['err_code'] = errors['illegal email address']
            response['err_msg'] = 'illegal email address'
            self.write(response)
            logging.info('input is not a valid email address')
            return
        else:
            token = Encryption.encode({'email': email, 'expiration_time': str(datetime.datetime.now())})
            logging.info('/auth/reset_password?'+token)
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            self.write(response)

