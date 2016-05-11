__author__ = 'TianluWang'

import MySQLdb
import logging
import auth.config


class MySQLOperation:
    """manage database"""

    def __init__(self, mysql):
        self.mysql = mysql
        self.conn = None

    def is_connected(self):
        try:
            self.conn.ping()
        except Exception, e:
            logging.info('database connection has gone away')
            return False
        else:
            return True

    def connect(self):
        try:
            db = MySQLdb.connect(host=self.mysql['host'], user=self.mysql['user'], passwd=self.mysql['passwd'],
                                 db=self.mysql['db'], port=int(self.mysql['port']),
                                 connect_timeout=self.mysql['connect_timeout'], charset='utf8')
        except Exception, e:
            logging.error('connect database fails')
            raise
        else:
            self.conn = db

    def execute(self, cmd):
        if self.is_connected():
            pass
        else:
            self.connect()
            logging.info('database reconnect')

        cursor = self.conn.cursor()
        try:
            cursor.execute(cmd)
        except Exception, e:
            logging.error(cmd + 'fails')
            raise
        else:
            self.conn.commit()
            return cursor.fetchall()

conn = MySQLOperation(auth.config.mysql)