import os
import subprocess
import sys
import time
from optparse import OptionParser

from ASAN.asan import Asan
from dict import sanitizer_name

if __name__ == '__main__':

    args = sys.argv[1:]

    usage = "1. crash-analysis.py -d crashed_dir -m default -s asan \"target_prog @@\" \n       " \
            "2. crash-analysis.py -d crashed_dir -m network -s asan -r \"tcpreplay ...\" " \
            "\"network_prog -p 1080 ...\""
    optParser = OptionParser(usage, version="%prog 1.0")

    optParser.add_option('-d', '--dir', type="string", dest='dir',
                         help="The directory of testcases which caused the target crash")
    optParser.add_option('-m', '--mode', type="string", dest='mode',
                         default="default", help="1. default: for normal target 2. network: for network application")
    optParser.add_option('-r', '--replay', type="string",
                         dest='cmd', help="Specify the replay application and options and send packets to target")
    optParser.add_option('-s', '--sanitizer', type="string", dest="sanitizer",
                         default="asan", help="Sanitizer which you instrument in target")

    option, args = optParser.parse_args(args)

    assert len(args) == 1 and option.dir is not None
    assert option.mode == 'default' or option.mode == 'network'

    target_cmd = args[0]
    replay_cmd = None

    prefix = ""
    suffix = ""

    sanitizer = sanitizer_name.get(option.sanitizer)
    assert sanitizer

    record = None

    if sanitizer == 'AddressSanitizer':
        prefix = "================================================================="
        suffix = "==ABORTING"
        record = Asan()

    if option.mode == 'network':
        assert option.cmd is not None
        replay_cmd = option.cmd

    not_crash = []
    assertion_fail = []

    if not replay_cmd:
        # for normal programme
        set_file = -1
        args = target_cmd.split(' ')

        for i in range(len(args)):
            if args[i] == '@@':
                set_file = i
                break

        work_path = args[0][:args[0].rfind('/')]
        # print(work_path)

        for root, dirs, files in os.walk(option.dir):
            for file in sorted(files):
                file_path = os.path.join(root, file)
                print(f"Now is process '{file}'...")
                if set_file == -1:
                    with open(file_path, "r") as fp:
                        ret = subprocess.run(args, stdin=fp, stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE, encoding="cp850", cwd=work_path)

                else:
                    args[set_file] = file_path
                    ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         encoding="cp850", cwd=work_path)

                if ret.returncode == 0:
                    print(f"File {file_path} seems not to lead crashing?")
                    not_crash.append(file_path)
                else:
                    # handle crashes
                    error_text = ret.stderr
                    if sanitizer not in error_text:
                        assertion_fail.append(file_path)
                    else:
                        error_text = error_text[error_text.find(prefix):error_text.find(suffix) + len(suffix) - 1]
                        record.add(error_text, file)

    else:
        server_cmd = target_cmd.split(' ')
        client_cmd = option.cmd.split(' ')

        set_file = -1
        for i in range(len(client_cmd)):
            if client_cmd[i] == '@@':
                set_file = i
                break

        work_path = server_cmd[0][:server_cmd[0].rfind('/')]

        for root, dirs, files in os.walk(option.dir):
            for file in sorted(files):
                file_path = os.path.join(root, file)
                print(f"Now is process '{file}'...")

                # start server
                server = subprocess.Popen(args=server_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          encoding="cp850", cwd=work_path)
                time.sleep(0.2)

                # replay the network packet
                if set_file == -1:
                    with open(file_path, "r") as fp:
                        client = subprocess.Popen(args=client_cmd, stdin=fp, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE, encoding="cp850", cwd=work_path)
                else:
                    client_cmd[set_file] = file_path
                    client = subprocess.Popen(args=client_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              encoding="cp850", cwd=work_path)
                time.sleep(1)

                # check if server crashed (timeout = 2s)
                for i in range(10):
                    if not subprocess.Popen.poll(server):
                        time.sleep(0.2)
                        continue
                    else:
                        break

                if subprocess.Popen.poll(server):
                    if server.returncode == 0:
                        print(f"File {file_path} seems not to lead crashing?")
                        not_crash.append(file)
                    else:
                        # handle crash
                        error_text = server.stderr.read()
                        if sanitizer not in error_text:
                            assertion_fail.append(file_path)
                        else:
                            error_text = error_text[error_text.find(prefix):error_text.find(suffix) + len(suffix) - 1]
                            record.add(error_text, file)
                else:
                    print(f"File {file_path} seems not to lead crashing?")
                    server.kill()
                    # not crash
                    not_crash.append(file)

                client.kill()

    print("\nResults: ")
    record.info()
    record.save()

    idx = 0
    for file in not_crash:
        if idx == 0:
            print("There files didn't crash: ")
        idx += 1
        print(f"File {idx}: {file}")

    idx = 0
    for file in assertion_fail:
        if idx == 0:
            print("There files are assertion failed: ")
        idx += 1
        print(f"File {idx}: {file}")
