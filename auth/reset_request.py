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

class ResetRequest:

    def get(self):
        