"""
This class include:
    stack-buffer-underflow
"""
from enum import Enum

from callstack import Callstack
from config import FUNCTION_SIMILAR, LOCATION_SIMILAR


class UnderflowType(Enum):
    stack = 1


class Underflow(object):
    def __init__(self, error_type, text, fname):
        self.error_type = error_type
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.operation = 0 if "READ" in text else 1  # 0 for read, 1 for write
        self.maybe_same = []
        self.total = 1
        self.files = [fname]

    def compare(self, underflow):
        assert underflow.__class__.__name__ == 'Underflow'

        if self.error_type != underflow.error_type or self.operation != underflow.operation:
            return 3

        f_score, l_score = self.callstack.compare(underflow.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > FUNCTION_SIMILAR and l_score > LOCATION_SIMILAR:
            # possible same
            return 1

        return 2
