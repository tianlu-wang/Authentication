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
from auth.config import errors, token_timedelta, mysql
from auth.token import Encryption
from auth.db import conn


class LogInHangdler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error',
                    'result': {'account': 'null', 'user_name': 'null', 'token': 'null'}}
        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return
        account = payload.get('param', {}).get('account', '').lower()
        passwd = payload.get('param', {}).get('passwd', '').lower()
        logging.info('account and user_name and passwd in payload: ' + account + ' ' + passwd)
        
        select_sql = "select account, passwd, uid, user_name from %s where account = '%s'" %\
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
            return
        if select_result[0][1] == passwd:
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            expiration_time = datetime.datetime.now() + token_timedelta
            token = Encryption.encode({'uid': select_result[0][2], 'expiration_time': str(expiration_time), 'type': 'log_in'})
            response['result'] = {'account': account, 'user_name': select_result[0][3], 'token': token}
            self.write(tornado.escape.json_encode(response))

            update_logintime_sql = "update %s set last_login_time=now() where account='%s'" % \
                                   (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account))
            try:
                conn.execute(update_logintime_sql)
                logging.info('update last log in time')
            except Exception, e:
                self.write(tornado.escape.json_encode(response))
                logging.error(traceback.format_exc())
                return
            return
        else:
            response['err_code'] = errors['incorrect password']
            response['err_msg'] = 'incorrect password'
            self.write(tornado.escape.json_encode(response))
            return


