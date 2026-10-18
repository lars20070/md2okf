#!/usr/bin/env python3
"""Explore Pi session traces with bounded, allowlisted output."""

import os
import sys

from pi_trace_commands import main

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except AttributeError:
            pass
    try:
        code = main(prog=os.path.basename(sys.argv[0]))
        sys.stdout.flush()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        code = 0
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)
