import datetime
import os

from ASAN.alloc import AllocType, Alloc
from ASAN.overflow import Overflow, OverflowType
from ASAN.segv import Segv
from debug import color
from dict import errors_name
from undefined import Undefined


class Asan(object):
    def __init__(self):
        self.overflow = []
        self.segv = []
        self.uax = []
        self.alloc = []
        self.undefined = []

        self.parseFunctions = {
            "heap-buffer-overflow": self.__parse_overflow,
            "stack-buffer-overflow": self.__parse_overflow,
            "dynamic-stack-buffer-overflow": self.__parse_overflow,
            "global-buffer-overflow": self.__parse_overflow,
            "container-overflow": self.__parse_overflow,
            "SEGV": self.__parse_segv,
            "out-of-memory": self.__parse_alloc,
            "alloc-dealloc-mismatch": self.__parse_alloc,
            "allocation-size-too-big": self.__parse_alloc,
            "undefined": self.__parse_undefined,
        }
        # ... add other bugs

    def add(self, text, fname):

        exist = False

        name = ""

        for item in errors_name['ASAN']:
            if item in text:
                name = item
                exist = True
                break

        if not exist:
            # This type error cannot parse for now ...
            name = "undefined"

        self.parseFunctions[name](name, text, fname)

    def __handle_new_object(self, objects_list, obj, fname):

        i = len(objects_list) - 1

        while i >= 0:
            item = objects_list[i]
            flag = item.compare(obj)

            if flag == 0:
                item.total += 1
                item.files.append(fname)
                break
            elif flag == 1:
                j = len(item.maybe_same) - 1

                while j >= 0:
                    obj1 = item.maybe_same[j]

                    if obj1.compare(obj) == 0:
                        obj1.total += 1
                        obj1.files.append(fname)
                        break
                    j -= 1

                if j == -1:
                    item.maybe_same.append(obj)
                break
            i -= 1

        if i == -1:
            objects_list.append(obj)

    def __parse_overflow(self, name, text, fname):

        error_type = -1

        if name == "heap-buffer-overflow":

            error_type = OverflowType.heap

        elif name == "stack-buffer-overflow":

            error_type = OverflowType.stack

        elif name == "dynamic-stack-buffer-overflow":

            error_type = OverflowType.dynamic_stack

        elif name == "global-buffer-overflow":

            error_type = OverflowType.global_buffer

        elif name == "container-overflow":

            error_type = OverflowType.container

        assert error_type != -1

        overflow_obj = Overflow(error_type, text, fname)

        if len(self.overflow) == 0:
            self.overflow.append(overflow_obj)
        else:
            self.__handle_new_object(self.overflow, overflow_obj, fname)

            '''
            for item in self.overflow:
                flag = item.compare(overflow_obj)
                if flag == 0:
                    item.total += 1
                    break
                elif flag == 1:
                    same = False
                    for obj in item.maybe_same:
                        if obj.compare(overflow_obj) == 0:
                            obj.total += 1
                            same = True
                            break
                    if not same:
                        item.maybe_same.append(overflow_obj)
                    break
            if flag != 0 and flag != 1:
                self.overflow.append(overflow_obj)
            '''

    def __parse_segv(self, name, text, fname):

        assert name == "SEGV"

        segv_object = Segv(text, fname)

        if len(self.segv) == 0:
            self.segv.append(segv_object)
        else:
            self.__handle_new_object(self.segv, segv_object, fname)

    def __parse_alloc(self, name, text, fname):

        error_type = -1

        if name == "alloc-dealloc-mismatch":

            error_type = AllocType.alloc_dealloc_mismatch

        elif name == "out-of-memory":

            error_type = AllocType.out_of_memory

        elif name == "allocation-size-too-big":

            error_type = AllocType.allocation_size_too_big

        assert error_type != -1

        alloc_object = Alloc(error_type, text, fname)

        if len(self.alloc) == 0:
            self.alloc.append(alloc_object)
        else:
            self.__handle_new_object(self.alloc, alloc_object, fname)

    def __parse_undefined(self, name, text, fname):

        assert name == 'undefined'

        undefined_object = Undefined(text, fname)
        self.undefined.append(undefined_object)

    def print_info(self, obj, padding):

        print(f"{padding}Call stack: {obj.callstack}")
        print(f"{padding}File: {color.GREEN_BKG}{list(obj.files)[0]}{color.END}" +
              (", ..." if len(obj.files) > 1 else ""))
        print(f"{padding}occurrence: {obj.total}")
        print(f"{padding}Maybe Same:")
        padding1 = padding + " " * 6
        print(f"{padding1}" + f"Total: {len(obj.maybe_same)}")

        idx = 0
        while idx < len(obj.maybe_same):
            obj1 = obj.maybe_same[idx]

            print(f"{padding1}No.{idx + 1} ==> Call stack: {obj1.callstack}")
            padding2 = padding1 + " " * len(f"No.{idx + 1} ==> ")
            print(f"{padding2}File: {color.GREEN_BKG}{list(obj1.files)[0]}{color.END}" +
                  (", ..." if len(obj1.files) > 1 else ""))

            if idx != len(obj.maybe_same) - 1:
                print(f"{padding1}" + "-" * 84)

            idx += 1

    def info(self):

        if len(self.overflow) != 0:
            idx = 0

            print(f"{color.PURPLE}Different overflow: {len(self.overflow)}{color.END}")
            while idx < len(self.overflow):

                overflow_obj = self.overflow[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}{overflow_obj.error_type.name}_overflow{color.END}")
                padding = " " * len(f"No.{idx + 1} ==> ")
                print(padding + f"Operate: {color.BLUE}" + ("READ" if overflow_obj.operation == 0 else "WRITE")
                      + f"{color.END}")
                self.print_info(overflow_obj, padding)

                if idx != len(self.overflow) - 1:
                    print("-" * 100)

                idx += 1

        print("*" * 100)
        print("*" * 100)

        if len(self.segv) != 0:
            idx = 0

            print(f"{color.PURPLE}Different SEGV: {len(self.segv)}{color.END}")
            while idx < len(self.segv):

                segv_obj = self.segv[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}SEGV{color.END}")
                padding = " " * len(f"No.{idx + 1} ==> ")
                self.print_info(segv_obj, padding)

                if idx != len(self.segv) - 1:
                    print("-" * 100)

                idx += 1

        print("*" * 100)
        print("*" * 100)

        if len(self.alloc) != 0:
            idx = 0

            print(f"{color.PURPLE}Different Alloc: {len(self.alloc)}{color.END}")
            while idx < len(self.alloc):

                alloc_obj = self.alloc[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}{alloc_obj.error_type.name}{color.END}")
                padding = " " * len(f"No.{idx + 1} ==> ")
                self.print_info(alloc_obj, padding)

                if idx != len(self.alloc) - 1:
                    print("-" * 100)

                idx += 1

        print("*" * 100)
        print("*" * 100)

    def save(self):

        save_path = "output_asan_" + str(int(datetime.datetime.now().timestamp()))
        os.mkdir(save_path)

        error_type = {
            'Overflow': self.overflow,
            "SEGV": self.segv,
            "Uax": self.uax,
            "Alloc": self.alloc,
            "Undefined": self.undefined
        }

        for name in error_type.keys():
            sub_dir = os.path.join(save_path, name)
            os.mkdir(sub_dir)

        for name, objs in error_type.items():
            sub_dir = os.path.join(save_path, name)
            idx = 0

            for obj in objs:
                idx += 1
                dir_n = ""
                if obj.__class__.__name__ == 'Overflow':
                    dir_n = f"#{idx}-{obj.error_type.name}_overflow"
                elif obj.__class__.__name__ == 'Segv':
                    dir_n = f"#{idx}-segv"
                elif obj.__class__.__name__ == 'Alloc':
                    dir_n = f"#{idx}-{obj.error_type.name}_overflow"
                elif obj.__class__.__name__ == 'Undefined':
                    dir_n = f"#{idx}-undefined"

                dir_n = os.path.join(sub_dir, dir_n)
                os.mkdir(dir_n)

                fn = os.path.join(dir_n, "result.txt")
                with open(fn, "w") as fp:
                    fp.write(obj.text)

                fn = os.path.join(dir_n, "callstack.txt")
                with open(fn, "w") as fp:
                    fp.write(obj.callstack.info())

                fn = os.path.join(dir_n, "files.txt")
                with open(fn, "w") as fp:
                    for f in obj.files:
                        fp.write(f + "\n")

                if len(obj.maybe_same) > 0:

                    dir_n = os.path.join(dir_n, "may_same")
                    os.mkdir(dir_n)

                    idx_1 = 0

                    for obj1 in obj.maybe_same:
                        idx_1 += 1

                        dir_1 = os.path.join(dir_n, f"#{idx_1}")
                        os.mkdir(dir_1)

                        fn = os.path.join(dir_1, "result.txt")
                        with open(fn, "w") as fp:
                            fp.write(obj1.text)

                        fn = os.path.join(dir_1, "callstack.txt")
                        with open(fn, "w") as fp:
                            fp.write(obj1.callstack.info())

                        fn = os.path.join(dir_1, "files.txt")
                        with open(fn, "w") as fp:
                            for f in obj1.files:
                                fp.write(f + "\n")
