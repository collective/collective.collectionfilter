# -*- coding: utf-8 -*-


class DictDataWrapper(object):

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError
