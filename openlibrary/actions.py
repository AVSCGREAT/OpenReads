"""Custom OL Actions.
"""
from __future__ import print_function

import sys

import infogami


@infogami.action
def runmain(modulename, *args):
    print("run_main", modulename, sys.argv)
    mod = __import__(modulename, globals(), locals(), modulename.split("."))
    mod.main(*args)
