from callstack import Callstack


class Segv(object):
    def __init__(self, text, fname):
        self.text = text
        self.callstack = Callstack(self.text.split("\n\n", 1)[0])
        self.operation = 0 if "READ" in text else 1  # 0 for read, 1 for write
        self.maybe_same = []
        self.total = 1
        self.files = [fname]

    def compare(self, segv):
        assert segv.__class__.__name__ == 'Segv'

        if self.operation != segv.operation:
            return 3

        f_score, l_score = self.callstack.compare(segv.callstack)

        if f_score == 1:
            # same stack (location may not same due to '-g' flag)
            return 0

        if f_score > 0.9 and l_score > 0.9:
            # possible same
            return 1

        return 2

