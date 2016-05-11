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
from auth.token import Encryption
from auth.db import conn


class LogInHangdler(tornado.web.RequestHandler):

    def post(self):
        response = {'err_code': 100, 'err_msg': 'other',
                    'result': {'account': 'null', 'user_name': 'null', 'token': 'null'}}
        try:
            payload = tornado.escape.json_decode(self.request.body)
        except Exception, e:
            self.write(response)
            logging.error(traceback.format_exc())
            return
        account = payload['param']['account']
        user_name = payload['param']['user_name']
        passwd = payload['param']['passwd']
        logging.info('account and user_name and passwd in payload: ' + account + ' ' + user_name + ' ' + passwd)
        
        select_sql = "select account, passwd, uid, user_name from userinfo_tbl where account = '%s'" % account
        try:
            select_result = conn.execute(select_sql)
            logging.info(select_result)
        except Exception, e:
            self.write(response)
            logging.error(traceback.format_exc())
            return
        if not select_result:
            response['err_code'] = 102
            response['err_msg'] = 'user not exists'
            self.write(tornado.escape.json_encode(response))
            return
        if select_result[0][1] == passwd:
            response['err_code'] = 0
            response['err_msg'] = 'success'
            expiration_time = datetime.datetime.now() + token_timedelta
            token = Encryption.encode({'uid': select_result[0][2], 'expiration_time': str(expiration_time)})
            response['result'] = {'account': account, 'user_name': select_result[0][3], 'token': token}

            self.write(tornado.escape.json_encode(response))
            return
        else:
            response['err_code'] = 101
            response['err_msg'] = 'incorrect password'
            self.write(tornado.escape.json_encode(response))
            return


