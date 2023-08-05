#!/usr/bin/env python3

import doctest
import os
import sys

import csx
import script


def _main():
    """Run all tests."""
    doctest.testmod(csx)
    doctest.testmod(script)
    try:
        base = os.path.relpath(sys.path[0])
    except ValueError:
        base = os.curdir
    for root, __, files in os.walk(base):
        for filename in files:
            if filename.endswith(".txt"):
                doctest.testfile(os.path.join(root, filename))


if __name__ == "__main__":
    sys.exit(_main())

