# Crash-analysis Tool for Fuzzing

This tool is written in Python, mainly focus on Address sanitizer output. For Now, the types of vulnerabilities based on Address sanitizer output supported by the tool for identification are following:

| Name                               |
| ---------------------------------- |
| heap-buffer-overflow               |
| stack-buffer-overflow              |
| dynamic-stack-buffer-overflow      |
| global-buffer-overflow             |
| container-overflow                 |
| SEGV                               |
| out-of-memory                      |
| alloc-dealloc-mismatch             |
| allocation-size-too-big            |
| bad-free                           |
| FPE（floating pointing exception） |
| unknown-crash                      |
| heap-use-after-free                |
| double-free                        |
| container-overflow                 |
| bad-malloc-usable-size             |
| calloc-overflow                    |

In the future, we will support more vulnerabilities in ASAN and vulnerabilities in other sanitizers (such as MASN).

## Usage

You can see usage by `--help` option like:

```bash
$ python3 crash-analysis.py --help
Usage: 1. crash-analysis.py -d crashed_dir -m default -s asan "target_prog @@" 
       2. crash-analysis.py -d crashed_dir -m network -s asan -r "tcpreplay ..." "network_prog -p 1080 ..."

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     The directory of testcases which caused the target
                        crash
  -m MODE, --mode=MODE  1. default: for normal target 2. network: for network
                        application
  -r CMD, --replay=CMD  Specify the replay application and options and send
                        packets to target
  -s SANITIZER, --sanitizer=SANITIZER
                        Sanitizer which you instrument in target
```

For normal target instrumented by address sanitizer, you can use like:

```bash
$ python3 crash-analysis.py -d crash_dir -s asan "target_prog [-options] [@@]"
```

:chestnut:example:

```bash
$ python ./crashes-analysis.py -d /xxx/replayable-crashes -s asan "target1 @@"
```
```text
Now is process 'id:000103,sig:06,src:000000,op:havoc 1-3,rep:32'...
Now is process 'id:000074,sig:06,src:000000+000461,op:splice 0-3,rep:4'...
Now is process 'id:000104,sig:06,src:000000,op:havoc 1-3,rep:128'...
Now is process 'id:000312,sig:06,src:001930+000123,op:splice 0-3,rep:16'...
Now is process 'id:000363,sig:06,src:001802,op:havoc 2-3,rep:16'...
...
Now is process 'id:000059,sig:06,src:000000,op:havoc 0-3,rep:16'...
Now is process 'id:000409,sig:06,src:002633,op:havoc 1-3,rep:128'...

Results: 
Different overflow: 2
No.1 ==> Type: stack_overflow
         Operate: READ
         Call stack: <callstack.Callstack object at 0x7f3bbd09fb80>
         File: id:000363,sig:06,src:001802,op:havoc 2-3,rep:16, ...
         occurrence: 12
         Maybe Same:
               Total: 0
No.2 ==> Type: heap_overflow
         Operate: READ
         Call stack: <callstack.Callstack object at 0x7f3bbd047760>
         File: id:000271,sig:06,src:001544+000527,op:splice 0-3,rep:2, ...
         occurrence: 2
         Maybe Same:
               Total: 3
               No.1 ==> Call stack: <callstack.Callstack object at 0x7f3bbd047fd0>
                        File: id:000053,sig:06,src:000000,op:havoc 0-3,rep:8, ...
               ------------------------------------------------------------------------------------
               No.2 ==> Call stack: <callstack.Callstack object at 0x7f3bbd062340>
                        File: id:000281,sig:06,src:001544+000527,op:splice 0-3,rep:16
               ------------------------------------------------------------------------------------
               No.3 ==> Call stack: <callstack.Callstack object at 0x7f3bbd062970>
                        File: id:000404,sig:06,src:002240+002812,op:splice 0-3,rep:2
****************************************************************************************************
****************************************************************************************************
Different SEGV: 1
No.1 ==> Type: SEGV
         Call stack: <callstack.Callstack object at 0x7f3bbd09f9d0>
         File: id:000103,sig:06,src:000000,op:havoc 1-3,rep:32, ...
         occurrence: 13
         Maybe Same:
               Total: 4
               No.1 ==> Call stack: <callstack.Callstack object at 0x7f3bbd09f9a0>
                        File: id:000146,sig:06,src:000000,op:havoc 1-3,rep:2, ...
               ------------------------------------------------------------------------------------
               No.2 ==> Call stack: <callstack.Callstack object at 0x7f3bbd09ff70>
                        File: id:000180,sig:06,src:000010,op:havoc 1-3,rep:32
               ------------------------------------------------------------------------------------
               No.3 ==> Call stack: <callstack.Callstack object at 0x7f3bbd047e80>
                        File: id:000263,sig:06,src:001534,op:havoc 1-3,rep:64, ...
               ------------------------------------------------------------------------------------
               No.4 ==> Call stack: <callstack.Callstack object at 0x7f3bbd062430>
                        File: id:000345,sig:06,src:002266+002094,op:splice 1-3,rep:8, ...
****************************************************************************************************
****************************************************************************************************
Different Alloc: 1
No.1 ==> Type: out_of_memory
         Call stack: <callstack.Callstack object at 0x7f3bbd047700>
         File: id:000217,sig:06,src:000501,op:havoc 0-3,rep:8, ...
         occurrence: 8
         Maybe Same:
               Total: 0
****************************************************************************************************
****************************************************************************************************
There files didn't crash:
...
There files are assertion failed: 
...
```

---

For network program, you can use like:

```bash
$ python3 crash-analysis.py -d crash_dir -s asan -r "replay-tool [-options] [@@]" "network_prog [-options]"
```

:bulb: Note that the results will be saved in `output_asan_{timestamp}` directory under working directory.

## Issue

The unrecognized output will be saved under `undefined` directory under output directory. I will be happy if you report the `undefined` output for expanding resolvable items.