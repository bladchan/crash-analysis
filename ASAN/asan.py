import datetime
import os

from ASAN.alloc import AllocType, Alloc
from ASAN.others import Unknown_crash, FPE
from ASAN.overflow import Overflow, OverflowType
from ASAN.segv import Segv
from ASAN.uax import UaxType, Uax
from ASAN.underflow import Underflow, UnderflowType
from debug import color
from dict import errors_name
from undefined import Undefined


class Asan(object):
    def __init__(self):
        self.overflow = []
        self.underflow = []
        self.segv = []
        self.uax = []
        self.alloc = []
        self.undefined = []
        self.others = []

        self.parseFunctions = {
            "heap-buffer-overflow": self.__parse_overflow,
            "stack-buffer-overflow": self.__parse_overflow,
            "dynamic-stack-buffer-overflow": self.__parse_overflow,
            "global-buffer-overflow": self.__parse_overflow,
            "container-overflow": self.__parse_overflow,
            "calloc-overflow": self.__parse_overflow,
            "stack-buffer-underflow": self.__parse_underflow,
            "SEGV": self.__parse_segv,
            "out-of-memory": self.__parse_alloc,
            "alloc-dealloc-mismatch": self.__parse_alloc,
            "allocation-size-too-big": self.__parse_alloc,
            "bad-free": self.__parse_alloc,
            "double-free": self.__parse_alloc,
            "bad-malloc-usable-size": self.__parse_alloc,
            "undefined": self.__parse_undefined,
            "unknown-crash": self.__parse_others,
            "FPE": self.__parse_others,
            "heap-use-after-free": self.__parse_uax,
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

            if type(item) is not type(obj):
                i -= 1
                continue

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

        elif name == "calloc-overflow":

            error_type = OverflowType.calloc

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

    def __parse_underflow(self, name, text, fname):

        error_type = -1

        if name == "stack-buffer-underflow":
            error_type = UnderflowType.stack

        assert error_type != -1

        underflow_obj = Underflow(error_type, text, fname)

        if len(self.underflow) == 0:
            self.underflow.append(underflow_obj)
        else:
            self.__handle_new_object(self.underflow, underflow_obj, fname)

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

        elif name == "bad-free":

            error_type = AllocType.bad_free

        elif name == "double-free":

            error_type = AllocType.double_free

        elif name == "bad-malloc-usable-size":

            error_type = AllocType.bad_malloc_usable_size

        assert error_type != -1

        alloc_object = Alloc(error_type, text, fname)

        if len(self.alloc) == 0:
            self.alloc.append(alloc_object)
        else:
            self.__handle_new_object(self.alloc, alloc_object, fname)

    def __parse_uax(self, name, text, fname):

        error_type = -1

        if name == 'heap-use-after-free':
            error_type = UaxType.heap_use_after_free

        assert error_type != -1

        uax_obj = Uax(error_type, text, fname)

        if len(self.uax) == 0:
            self.uax.append(uax_obj)
        else:
            self.__handle_new_object(self.uax, uax_obj, fname)

    def __parse_undefined(self, name, text, fname):

        assert name == 'undefined'

        undefined_object = Undefined(text, fname)
        self.undefined.append(undefined_object)

    def __parse_others(self, name, text, fname):

        obj = None

        if name == "unknown-crash":

            obj = Unknown_crash(text, fname)

        elif name == "FPE":

            obj = FPE(text, fname)

        assert obj

        if len(self.others) == 0:
            self.others.append(obj)
        else:
            self.__handle_new_object(self.others, obj, fname)

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

        print_flag = False

        if len(self.overflow) != 0:
            print_flag = True
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

        if print_flag:
            print("*" * 100)
            print("*" * 100)

        print_flag = False

        if len(self.underflow) != 0:
            print_flag = True
            idx = 0

            print(f"{color.PURPLE}Different underflow: {len(self.underflow)}{color.END}")
            while idx < len(self.underflow):

                underflow_obj = self.underflow[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}{underflow_obj.error_type.name}_underflow{color.END}")
                padding = " " * len(f"No.{idx + 1} ==> ")
                print(padding + f"Operate: {color.BLUE}" + ("READ" if underflow_obj.operation == 0 else "WRITE")
                      + f"{color.END}")
                self.print_info(underflow_obj, padding)

                if idx != len(self.underflow) - 1:
                    print("-" * 100)

                idx += 1

        if print_flag:
            print("*" * 100)
            print("*" * 100)

        print_flag = False

        if len(self.segv) != 0:
            print_flag = True
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

        if print_flag:
            print("*" * 100)
            print("*" * 100)

        print_flag = False

        if len(self.alloc) != 0:
            print_flag = True
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

        if print_flag:
            print("*" * 100)
            print("*" * 100)

        print_flag = False

        if len(self.uax) != 0:
            print_flag = True
            idx = 0

            print(f"{color.PURPLE}Different User-after-x: {len(self.uax)}{color.END}")

            while idx < len(self.uax):

                uax_obj = self.uax[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}{uax_obj.error_type.name}{color.END}")

                padding = " " * len(f"No.{idx + 1} ==> ")
                print(padding + f"Operate: {color.BLUE}" + ("READ" if uax_obj.operation == 0 else "WRITE")
                      + f"{color.END}")

                self.print_info(uax_obj, padding)

                if idx != len(self.uax) - 1:
                    print("-" * 100)

                idx += 1

        if print_flag:
            print("*" * 100)
            print("*" * 100)

        if len(self.others) != 0:
            print_flag = True
            idx = 0

            print(f"{color.PURPLE}Others: {len(self.others)}{color.END}")
            while idx < len(self.others):

                obj = self.others[idx]

                print(f"No.{idx + 1} ==> Type: {color.RED}{obj.__class__.__name__}{color.END}")
                padding = " " * len(f"No.{idx + 1} ==> ")

                if obj.__class__.__name__ == 'Unknown_crash':
                    print(padding + f"Operate: {color.BLUE}" + ("READ" if obj.operation == 0 else "WRITE")
                          + f"{color.END}")

                padding = " " * len(f"No.{idx + 1} ==> ")
                self.print_info(obj, padding)

                if idx != len(self.others) - 1:
                    print("-" * 100)

                idx += 1

    def save(self):

        save_path = "output_asan_" + str(int(datetime.datetime.now().timestamp()))
        os.mkdir(save_path)

        error_type = {
            'Overflow': self.overflow,
            'Underflow': self.underflow,
            "SEGV": self.segv,
            "Uax": self.uax,
            "Alloc": self.alloc,
            "Undefined": self.undefined,
            "Others": self.others,
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
                elif obj.__class__.__name__ == 'Underflow':
                    dir_n = f"#{idx}-{obj.error_type.name}_underflow"
                elif obj.__class__.__name__ == 'Segv':
                    dir_n = f"#{idx}-segv"
                elif obj.__class__.__name__ == 'Alloc':
                    dir_n = f"#{idx}-{obj.error_type.name}_overflow"
                elif obj.__class__.__name__ == 'Undefined':
                    dir_n = f"#{idx}-undefined"
                elif obj.__class__.__name__ == 'FPE':
                    dir_n = f"#{idx}-FPE"
                elif obj.__class__.__name__ == 'Unknown_crash':
                    dir_n = f"#{idx}-unknown-crash"
                elif obj.__class__.__name__ == 'Uax':
                    dir_n = f"#{idx}-{obj.error_type.name}"

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
