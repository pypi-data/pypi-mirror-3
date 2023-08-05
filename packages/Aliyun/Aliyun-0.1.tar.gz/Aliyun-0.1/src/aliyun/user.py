# -*- coding: utf-8 -*-

class User(object):
    def __init__(self, name):
        self.name = name
        
    def get_last_login_message(self):
        message = "Last login: %s from %s" % ("Sun Nov  6 22:52:49 2011", "115.193.187.227")
        return message
