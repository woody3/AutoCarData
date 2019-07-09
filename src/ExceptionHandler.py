# -*- coding: utf-8 -*-

class AutoCarException(Exception):
    def __init__(self, message):
        self.message = message