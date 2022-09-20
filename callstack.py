import re
import difflib
from texttable import Texttable

# regex = r'#([0-9]+) 0x[0-9|a-f]+ in (.*) ([/|.|(].*)'
regex = r'#([0-9]+) 0x[0-9|a-f]+ ([in \S+]*) ([/|.|(].*)'


class Callstack(object):
    def __init__(self, text):
        self.stack = []
        self.size = 0
        pre_frame = -1

        result = re.findall(regex, text)
        assert len(result) != 0

        for (frame, function, location) in result:
            if len(function) != 0:
                function = function[3:]
            self.stack.append((frame, function, location))
            self.size += 1

            # print(f"frame = {frame}, function = {function}, location = {location}")

            # check if meet frame continuity
            assert pre_frame + 1 == int(frame)
            pre_frame = int(frame)

    def getStack(self):
        return self.stack

    def compare(self, callstack):
        assert callstack.__class__.__name__ == 'Callstack'

        f_score = 0
        l_score = 0

        if self.size == callstack.size:
            # high possibility the same callstack
            for i in range(0, self.size):
                f_score += difflib.SequenceMatcher(None, self.stack[i][1], callstack.stack[i][1]).quick_ratio()
                l_score += difflib.SequenceMatcher(None, self.stack[i][2], callstack.stack[i][2]).quick_ratio()

            f_score = f_score / self.size
            l_score = l_score / self.size

            return f_score, l_score
        else:
            # maybe has the same frames
            i = self.size - 1
            j = callstack.size - 1

            while i >= 0 and j >= 0:
                f_score += difflib.SequenceMatcher(None, self.stack[i][1], callstack.stack[j][1]).quick_ratio()
                l_score += difflib.SequenceMatcher(None, self.stack[i][2], callstack.stack[j][2]).quick_ratio()

                i -= 1
                j -= 1

            f_score = f_score / max(self.size - 1, callstack.size - 1)
            l_score = l_score / max(self.size - 1, callstack.size - 1)

            return f_score, l_score

    def info(self):
        table = Texttable()
        table.add_row(["frame", "function", "location"])
        table.set_cols_width([5, 50, 50])
        for item in self.stack:
            table.add_row(list(item))

        return table.draw()
