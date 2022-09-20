'''
This class is used for undefined
'''
from callstack import Callstack


class Undefined(object):
    def __init__(self, text, fname):
        self.text = text
        self.files = [fname]
        self.callstack = Callstack("")
        self.maybe_same = []
