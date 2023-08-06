#!/usr/bin/env python

import sys
import os.path
import traceback


try:
    import readline
except ImportError:
    pass
else:
    import os
    import atexit
    histfile = os.path.join(os.path.expanduser("~"), ".clojurepyhist")
    try:
        readline.read_history_file(histfile)
    except IOError:
        # Pass here as there isn't any history file, so one will be
        # written by atexit
        pass
    atexit.register(readline.write_history_file, histfile)

import __builtin__
import sys
import os.path

_old_import_ = __builtin__.__import__
def import_hook(name, globals=None, locals=None, fromlist=None, level = -1):
    try:
        return _old_import_(name, globals, locals, fromlist, level)
    except ImportError:
        pass

    conv = name.replace(".", "/")
    for p in ["."] + sys.path:
        f = p + "/" + conv + ".clj"
        if os.path.exists(f):
            requireClj(f)
            try:
                return _old_import_(name, globals, locals, fromlist, level)
            except ImportError:
                raise ImportError("could not find module " + name + " after loading " + f)

    raise ImportError("module " + name + " not found")

__builtin__.__import__ = import_hook

from clojure.lang.lispreader import read
from clojure.lang.fileseq import StringReader
from clojure.lang.globals import currentCompiler
import clojure.lang.rt as RT
from clojure.lang.compiler import Compiler
from clojure.lang.symbol import Symbol, symbol
import cPickle

VERSION = "0.1.0g"



def requireClj(filename, stopafter=None):
    with open(filename) as fl:
        r = StringReader(fl.read())

    RT.init()
    comp = Compiler()
    comp.setFile(filename)
    currentCompiler.set(comp)

    #o = open(filename+".cljc", "w")

    try:
        while True:
            s = read(r, True, None, True)
            #cPickle.dump(s, o)
            try:
                res = comp.compile(s)
                comp.executeCode(res)
                if stopafter is not None:
                    if hasattr(comp.getNS(), stopafter):
                        break
            except IOError as exp:
                print s
                raise exp

            while True:
                ch = r.read()

                if ch == "":
                    raise IOError()

                if ch not in [" ", "\t", "\n", "\r"]:
                    r.back()
                    break
    except IOError as e:
        pass

    #o.close()

#requireClj(os.path.dirname(__file__) + "/core.clj")
import clojure.core

def main():
    RT.init()
    comp = Compiler()
    currentCompiler.set(comp)
    comp.setNS(symbol("user"))

    if not sys.argv[1:]:
        while True:
            try:
                line = raw_input(comp.getNS().__name__ + "=> ")
            except EOFError:
                break

            if not line:
                continue

            while unbalanced(line):
                try:
                    line += raw_input('.' * len(comp.getNS().__name__) + '.. ')
                except EOFError:
                    break

            # Propogate break from above loop.
            if unbalanced(line):
                break

            r = StringReader(line)
            s = read(r, True, None, True)

            try:
                res = comp.compile(s)
                print comp.executeCode(res)
            except Exception:
                traceback.print_exc()
    else:
        for x in sys.argv[1:]:
            requireClj(x)


def unbalanced(s):
    return (s.count('(') != s.count(')')
            or s.count('[') != s.count(']')
            or s.count('{') != s.count('}'))


if __name__ == "__main__":
    main()
