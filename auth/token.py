__author__ = 'TianluWang'

from jose import jwt
import auth.config


class Token:
    def __init__(self, secret, algorithm):
        self.secret = secret
        self.algorithm = algorithm

    def encode(self, json_object):
        return jwt.encode(json_object, self.secret, self.algorithm)

    def decode(self, token):
        return jwt.decode(token, self.secret, self.algorithm)

Encryption = Token(auth.config.secret, auth.config.algorithm)

