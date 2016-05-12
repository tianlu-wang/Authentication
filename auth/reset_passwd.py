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
            token = Encryption.decode(self.request.query)
        except Exception, e:
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

        type = token.get('type', '')
        if type != 'reset':
            response['err_code'] = errors['illegal user']
            response['err_msg'] = 'illegal user'
            self.write(tornado.escape.json_encode(response))
            logging.info('incorrect token type')
            return

        uid = token.get('uid', 0)
        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return
        account = payload.get('param', {}).get('account', '').lower()
        passwd = payload.get('param', {}).get('passwd', '').lower()
        if passwd == '':
            response['err_code'] = errors['input cannot be null']
            response['err_msg'] = 'input cannot be null'
            self.write(tornado.escape.json_encode(response))
            logging.info('account and passwd in payload: ' + account + ' ' + passwd)
            return


        select_sql = "select account, uid, user_name from %s where account = '%s'" % \
                     (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account))
        try:
            select_result = conn.execute(select_sql)
            logging.info(select_result)
        except Exception, e:
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
            if uid != select_result[0][1]:
                response['err_code'] = errors['incorrect account']
                response['err_msg'] = 'incorrect account'
                self.write(tornado.escape.json_encode(response))
                logging.info('account and email do ont match')
                return
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
            token = Encryption.encode({'uid': select_result[0][1], 'expiration_time': str(expiration_time), 'type': 'log_in'})
            response['result'] = {'account': account, 'user_name': select_result[0][2], 'token': token}
            self.write(tornado.escape.json_encode(response))
            return