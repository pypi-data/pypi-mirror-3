# -*- coding: utf-8 -*-
from hashlib import sha256
from user import User

def authenticate(username, password):
    if username == 'aliyun' and password == 'a':
        return User(name = 'aliyun')
    else:
        return None

class Authentication(object):
    def __init__(self):
        self.username = None
        self.password = None
        pass

    def username(self, username):
        self.username = username

    def password(self, password):
        self.password = sha256(password).hexdigest()

    def login(self):
        pass

    def logout(self):
        self.__init__()
        pass

    def switch_user(self, username, password):
        self.username(username)
        self.password(password)
        return self.login()

    def check_permission(self, item):
        """
        If service provides permission list, then we are going to cache it 
        here to do a local permission check before sending to the server to
        cut down the network communication.
        """
        return False

