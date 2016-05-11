__author__ = 'TianluWang'

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import datetime
import logging
import traceback
import MySQLdb
from auth.token import Encryption
from auth.config import mysql, errors, token_timedelta
from auth.db import conn

class ResetPasswdHandler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error',
                    'result': {'account': 'null', 'user_name': 'null', 'token': 'null'}}

        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return
        account = payload['param']['account']
        passwd = payload['param']['passwd']
        logging.info('account and passwd in payload: ' + account + ' ' + passwd)

        select_sql = "select account, uid, user_name from %s where account = '%s'" % \
                     (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account))
        try:
            select_result = conn.execute(select_sql)
            logging.info(select_result)
        except Exception,e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return
        if not select_result:
            response['err_code'] = errors['user not exists']
            response['err_msg'] = 'user not exists'
            self.write(tornado.escape.json_encode(response))
            logging.info('user not exists')
            return
        else:
            reset_passwd_sql = "update %s set passwd='%s' where account='%s'" % \
                               (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(passwd),
                                MySQLdb.escape_string(account))
            try:
                conn.execute(reset_passwd_sql)
            except Exception, e:
                self.write(tornado.escape.json_encode(response))
                logging.error(traceback.format_exc())
                return
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'

            expiration_time = datetime.datetime.now() + token_timedelta
            token = Encryption.encode({'uid': select_result[0][1], 'expiration_time': str(expiration_time)})
            response['result'] = {'account': account, 'user_name': select_result[0][2], 'token': token}
            self.write(tornado.escape.json_encode(response))
            return