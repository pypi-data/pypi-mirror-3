#! /usr/bin/env python3

import os
import sys
import warnings

import script

BASE = os.path.abspath(os.path.dirname(sys.argv[0]))

def clean_tree():
    """Remove junk files from the working tree."""
    for root, __, files in os.walk(BASE):
        for filename in files:
            filepath = os.path.relpath(os.path.join(root, filename))
            basename, ext = os.path.splitext(filename)
            if ext in {".test", ".pyc"}:
                os.remove(filepath)
            if ext.startswith(".~"):
                warnings.warn("found {0!r}".format(filepath))

def update_script_usage():
    """Update the docstring for scripts/csx to show the usage message."""
    script_path = os.path.join(BASE, "csx")
    with open(script_path, "r") as f:
        parts = f.read().split('"""')
    parser = script.Parser()
    prog_name = parser.get_prog_name()
    parts[1] = parser.format_help().replace(prog_name, "csx") + "\n"
    with open(script_path, "w") as f:
        f.write('"""'.join(parts))

if __name__ == "__main__":
    warnings.simplefilter("always")
    clean_tree()
    update_script_usage()
