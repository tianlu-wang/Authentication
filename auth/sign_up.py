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
from auth.config import token_timedelta, errors, mysql
from auth.token import Encryption
from auth.db import conn


class SignUpHandler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error',
                    'result': {'account': 'null', 'user_name': 'null', 'token': 'null'}}
        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(logging.error(traceback.format_exc()))
            return

        account = payload.get('param', {}).get('account', '').lower()
        user_name = payload.get('param', {}).get('user_name', '').lower()
        passwd = payload.get('param', {}).get('passwd', '').lower()

        if account == '' or user_name == '' or passwd == '':
            response['err_code'] = errors['input cannot be null']
            response['err_msg'] = 'input cannot be null'
            self.write(tornado.escape.json_encode(response))
            logging.info('input cannot be null')
            return

        logging.info('account and passwd in payload: '+ account + ' ' + user_name + ' ' + passwd)

        select_sql = "select account from %s where account = '%s'" % \
                     (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account))
        try:
            select_result = conn.execute(select_sql)
            logging.info(select_result)
        except Exception, e:
            self.write(tornado.escape.json_encode(response))
            logging.error(traceback.format_exc())
            return
        if not select_result:
            try:
                print account+"#######"+passwd+"#########"+user_name
                insert_sql = "insert into %s(account, passwd, email, user_name) values " \
                             "('%s', '%s', '%s', '%s')" % \
                             (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account),
                              MySQLdb.escape_string(passwd),
                              MySQLdb.escape_string(account), MySQLdb.escape_string(user_name))  # TODO: account may be phone number
                conn.execute(insert_sql)
            except Exception, e:
                logging.error(traceback.format_exc())
                self.write(tornado.escape.json_encode(response))
                return
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            try:
                uid = conn.execute("select uid from %s where account='%s'" %
                                   (MySQLdb.escape_string(mysql['table_name']), MySQLdb.escape_string(account)))
            except Exception, e:
                logging.error(traceback.format_exc())
                self.write(tornado.escape.json_encode(response))
                return
            expiration_time = datetime.datetime.now() + token_timedelta
            token = Encryption.encode({'uid': uid[0][0], 'expiration_time': str(expiration_time), 'type': 'log_in'})
            response['result'] = {'account': account, 'user_name': user_name, 'token': token}
            self.write(tornado.escape.json_encode(response))
            return
        else:
            response['err_code'] = errors['user already exists']
            response['err_msg'] = 'user already exists'
            self.write(tornado.escape.json_encode(response))
            return
