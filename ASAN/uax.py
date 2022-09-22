"""
This class include:
    heap-use-after-free
    stack-use-after-return
    stack-use-after-scope
    use-after-poison
"""
from enum import Enum

from callstack import Callstack


class UaxType(Enum):
    heap_use_after_free = 1


class Uax(object):
    def __init__(self, error_type, text, fname):
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.operation = 0 if "READ" in text else 1  # 0 for read, 1 for write
        self.maybe_same = []
        self.total = 1
        self.files = [fname]
        self.error_type = error_type

    def compare(self, uax):
        assert uax.__class__.__name__ == 'Uax'

        if self.error_type != uax.error_type or self.operation != uax.operation:
            return 3

        f_score, l_score = self.callstack.compare(uax.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > 0.9 and l_score > 0.9:
            # possible same
            return 1

        return 2
