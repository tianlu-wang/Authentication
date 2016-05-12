__author__ = 'TianluWang'

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import datetime
import logging
import MySQLdb
from auth.config import errors, mysql
from auth.token import Encryption
from auth.db import conn


class VerifyHandler(tornado.web.RequestHandler):

    def get(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error',
                    'result': {'account': 'null', 'uid': 'null'}}
        try:
            token = Encryption.decode(self.get_argument('token'))
            print token
        except Exception, e:
            response['err_code'] = errors['illegal user']
            response['err_msg'] = 'illegal user'
            self.write(tornado.escape.json_encode(response))
            logging.info('token verify failed')
            return

        type = token.get('type', '').lower()
        if type != 'log_in':
            response['err_code'] = errors['illegal user']
            response['err_msg'] = 'illegal user'
            self.write(tornado.escape.json_encode(response))
            logging.info('token verify failed')
            return

        expiration_time = datetime.datetime.strptime(token.get('expiration_time', ''), "%Y-%m-%d %H:%M:%S.%f")
        if expiration_time < datetime.datetime.now():
            response['err_code'] = errors['timeout']
            response['err_msg'] = 'timeout'
            self.write(tornado.escape.json_encode(response))
            logging.info('token timeout')
            return
        else:
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            uid = token['uid']
            response['result']['uid'] = uid
            account = conn.execute("select account from %s where uid='%d'" %
                                   (MySQLdb.escape_string(mysql['table_name']), uid))
            response['result']['account'] = account[0][0]
            self.write(tornado.escape.json_encode(response))
            logging.info('token verify succeed')
            return