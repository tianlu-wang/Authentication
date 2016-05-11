__author__ = 'TianluWang'

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import datetime
import logging
import traceback
from auth.config import token_timedelta
from auth.config import errors
from auth.token import Encryption
from auth.db import conn


class SignUpHandler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': errors['other error'], 'err_msg': 'other error',
                    'result': {'account': 'null', 'user_name': 'null', 'token': 'null'}}
        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(response)
            logging.error(logging.error(traceback.format_exc()))
            return
        account = payload['param']['account']
        user_name = payload['param']['user_name']
        passwd = payload['param']['passwd']
        logging.info('account and user_name and passwd in payload: '+ account + ' ' + user_name + ' ' + passwd)

        select_sql = "select account from userinfo_tbl where account = '%s'" % account
        try:
            select_result = conn.execute(select_sql)
            logging.info(select_result)
        except Exception, e:
            self.write(response)
            logging.error(traceback.format_exc())
            return
        if not select_result:
            try:
                insert_sql = "insert into userinfo_tbl(account, passwd, email, user_name, create_time, " \
                             "last_login_time, write_time) values " \
                             "('%s', '%s', '%s', '%s', now(), now(), now())" % \
                             (account, passwd, account, user_name)  # TODO: account may be phone number
                conn.execute(insert_sql)
            except Exception, e:
                logging.error(traceback.format_exc())
                self.write(tornado.escape.json_encode(response))
                return
            response['err_code'] = errors['success']
            response['err_msg'] = 'success'
            try:
                uid = conn.execute("select uid from userinfo_tbl where account='%s'" % account)
            except Exception, e:
                logging.error(traceback.format_exc())
                self.write(tornado.escape.json_encode(response))
                return
            expiration_time = datetime.datetime.now() + token_timedelta
            token = Encryption.encode({'uid': uid, 'expiration_time': str(expiration_time)})
            response['result'] = {'account': account, 'user_name': user_name, 'token': token}
            self.write(tornado.escape.json_encode(response))
            return
        else:
            response['err_code'] = errors['user already exists']
            response['err_msg'] = 'user already exists'
            self.write(tornado.escape.json_encode(response))
            return
