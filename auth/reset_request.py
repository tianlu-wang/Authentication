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
import MySQLdb
from auth.db import conn
from auth.token import Encryption
from auth.config import errors, mysql, reset_timedelta


class ResetRequestHandler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error'}

        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return

        email = payload.get('param', {}).get('email', '').lower()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            response['err_code'] = errors['illegal email address']
            response['err_msg'] = 'illegal email address'
            self.write(tornado.escape.json_encode(response))
            logging.info('input is not a valid email address')
            return
        else:
            try:
                test = "select uid from %s where email='%s'" % \
                       (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(email))
                print test
                uid = conn.execute(test)
                uid = uid[0][0]
                logging.info('the email address %s belongs to user %d' % (email, uid))
            except Exception,e:
                response['err_code'] = errors['user not exists']
                response['err_msg'] = 'user not exists'
                self.write(tornado.escape.json_encode(response))
                logging.info('cannot find the uid according to the email address')
                return
            token = Encryption.encode({'uid': uid, 'expiration_time': str(datetime.datetime.now() + reset_timedelta), 'type': 'reset'})
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            self.write(tornado.escape.json_encode(response))
            logging.info(token)
            return

