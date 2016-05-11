__author__ = 'TianluWang'

import datetime

default_port = 8000
mysql = {'host': 'localhost',
         'user': 'root',
         'passwd': '123',
         'db': 'TORNADO',
         'port': 3306,
         'connect_timeout': 3}
secret = 'password'
algorithm = 'HS256'
token_timedelta = datetime.timedelta(days=1)