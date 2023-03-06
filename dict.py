
errors_name = {
    'ASAN': [
        "alloc-dealloc-mismatch",           # --> Class: alloc
        "out-of-memory",                    # --> Class: alloc
        "calloc-overflow",                  # --> Class: overflow
        "container-overflow",               # --> Class: overflow
        "double-free",                      # --> Class: alloc
        "dynamic-stack-buffer-overflow",    # --> Class: overflow
        "global-buffer-overflow",           # --> Class: overflow
        "heap-buffer-overflow",             # --> Class: overflow
        "heap-use-after-free",              # --> Class: uax
        # "invalid-allocation-alignment",
        # "memcpy-param-overlap",
        # "new-delete-type-mismatch",
        "SEGV",                             # --> Class: segv
        "stack-buffer-overflow",            # --> Class: overflow
        "stack-buffer-underflow",           # --> Class: underflow
        "stack-use-after-return",           # --> Class: uax
        "stack-use-after-scope",            # --> Class: uax
        # "strncat-param-overlap",
        "use-after-poison",                 # --> Class: uax
        "bad-free",                         # --> Class: alloc
        "allocation-size-too-big",          # --> Class: alloc
        "unknown-crash",                    # --> Class: Unknown_crash (in others.py)
        "FPE",                              # --> Class: FPE (floating point exception / in others.py)
        "bad-malloc-usable-size",           # --> Class: alloc
    ]
}

sanitizer_name = {
    "asan": "AddressSanitizer",
}
