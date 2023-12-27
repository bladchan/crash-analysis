from callstack import Callstack
from config import FUNCTION_SIMILAR, LOCATION_SIMILAR


class Unknown_crash(object):
    def __init__(self, text, fname):
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.operation = 0 if "READ" in text else 1  # 0 for read, 1 for write
        self.maybe_same = []
        self.total = 1
        self.files = [fname]

    def compare(self, unknown_crash):

        assert unknown_crash.__class__.__name__ == 'Unknown_crash'

        if self.operation != unknown_crash.operation:
            return 3

        f_score, l_score = self.callstack.compare(unknown_crash.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > FUNCTION_SIMILAR and l_score > LOCATION_SIMILAR:
            # possible same
            return 1

        return 2


class FPE(object):
    def __init__(self, text, fname):
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.maybe_same = []
        self.total = 1
        self.files = [fname]

    def compare(self, fpe):

        assert fpe.__class__.__name__ == 'FPE'

        f_score, l_score = self.callstack.compare(fpe.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > FUNCTION_SIMILAR and l_score > LOCATION_SIMILAR:
            # possible same
            return 1

        return 2
