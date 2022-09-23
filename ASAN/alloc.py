from enum import Enum

from callstack import Callstack


class AllocType(Enum):
    out_of_memory = 1
    alloc_dealloc_mismatch = 2
    allocation_size_too_big = 3
    bad_free = 4
    double_free = 5


class Alloc(object):
    def __init__(self, error_type, text, fname):
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.maybe_same = []
        self.total = 1
        self.files = [fname]
        self.error_type = error_type

    def compare(self, segv):
        assert segv.__class__.__name__ == 'Alloc'

        if self.error_type != segv.error_type:
            return 3

        f_score, l_score = self.callstack.compare(segv.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > 0.9 and l_score > 0.9:
            # possible same
            return 1

        return 2
