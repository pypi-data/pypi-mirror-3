from clojure.lang.ifn import IFn
from clojure.lang.cljexceptions import AbstractMethodCall
from clojure.lang.itransientmap import ITransientMap
import clojure.lang.rt as RT
from clojure.lang.iprintable import IPrintable

class ATransientMap(IFn, ITransientMap, IPrintable):
    def ensureEditable(self):
        raise AbstractMethodCall(self)

    def doAssoc(self, key, val):
        raise AbstractMethodCall(self)

    def doWithout(self, key):
        raise AbstractMethodCall(self)

    def doValAt(self, key, notFound = None):
        raise AbstractMethodCall(self)

    def doCount(self):
        raise AbstractMethodCall(self)

    def doPersistent(self):
        raise AbstractMethodCall(self)

    def conj(self, val):
        self.ensureEditable()
        return RT.conjToAssoc(self, val)

    def __call__(self, *args):
        return apply(self.valAt, args)

    def without(self, key):
        self.ensureEditable()
        return self.doWithout()

    def valAt(self, key, notFound = None):
        self.ensureEditable()
        return self.doValAt(key, notFound)

    def assoc(self, key, value):
        self.ensureEditable()
        return self.doAssoc(key, value)

    def count(self):
        self.ensureEditable()
        return self.count()

    def persistent(self):
        self.ensureEditable()
        return self.persistent()

    def writeAsString(self, writer):
        writer.write(repr(self))

    def writeAsReplString(self, writer):
        writer.write(repr(self))
