import types

from clojure.lang.iprintable import IPrintable
from clojure.lang.iobj import IObj
from clojure.lang.cljexceptions import ArityException
from clojure.lang.named import Named


class Symbol(IObj, IPrintable, Named):
    def __init__(self, *args):
        if len(args) == 2:
            self.ns = args[0].name if isinstance(args[0], Symbol) else args[0]
            self.name = args[1]
            self._meta = None
        elif len(args) == 3:
            self._meta = args[0]
            self.ns = args[1]
            self.name = args[2]
        else:
            raise ArityException()
        if isinstance(self.ns, types.ModuleType):
            pass

    def getNamespace(self):
        return self.ns

    def getName(self):
        return self.name

    def withMeta(self, meta):
        if meta is self.meta():
            return self
        return Symbol(meta, self.ns, self.name)

    def meta(self):
        return self._meta

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Symbol):
            return False
        return (self.ns == other.ns) and (self.name == other.name)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name) ^ hash(self.ns)

    def writeAsString(self, writer):
        writer.write(repr(self))

    def writeAsReplString(self, writer):
        writer.write(repr(self))

    def __repr__(self):
        if self.ns is None:
            return self.name
        else:
            return self.ns + "/" + self.name


def symbol(*args):
    if len(args) == 1:
        a = args[0]
        if isinstance(a, Symbol):
            return a
        idx = a.rfind("/")
        if idx == -1 or a == "/":
            return Symbol(None, a)
        else:
            return Symbol(a[idx:], a[:idx + 1])
    elif len(args) == 2:
        return Symbol(args[0], args[1])
    else:
        raise ArityException()
