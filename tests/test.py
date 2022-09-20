from ASAN.asan import Asan


if __name__ == '__main__':

    asan = Asan()

    with open('demo0.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo0.txt')

    with open('demo1.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo1.txt')

    with open('demo2.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo2.txt')

    with open('demo3.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo3.txt')

    with open('demo4.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo4.txt')

    with open('demo5.txt') as fp:
        content = fp.read()

    asan.add(content, 'demo5.txt')
    asan.info()
    asan.save()
