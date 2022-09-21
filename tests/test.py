import os

from ASAN.asan import Asan


if __name__ == '__main__':

    asan = Asan()

    for file in os.listdir(os.getcwd()):
        if '.txt' not in file:
            continue

        with open(file, 'r') as fp:
            content = fp.read()

        asan.add(content, file)

    asan.info()
    asan.save()
