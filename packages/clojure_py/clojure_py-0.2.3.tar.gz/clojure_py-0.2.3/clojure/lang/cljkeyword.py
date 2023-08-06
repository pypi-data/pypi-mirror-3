from clojure.lang.symbol import Symbol, symbol
from clojure.lang.persistenthashmap import EMPTY as EMPTY_MAP
from clojure.lang.atomicreference import AtomicReference
from clojure.lang.cljexceptions import InvalidArgumentException, ArityException
from clojure.lang.iprintable import IPrintable
import weakref
from clojure.lang.ifn import IFn
from clojure.lang.named import Named

interned = AtomicReference(EMPTY_MAP)

class Keyword(IFn, Named, IPrintable):
    def getNamespace(self):
        return self.sym.getNamespace()

    def getName(self):
        return self.sym.getName()
        
    def writeAsString(self, writer):
        writer.write(repr(self))

    def writeAsReplString(self, writer):
        writer.write(repr(self))

    def __init__(self, sym):
        self.sym = sym
        self.hash = hash(sym) + 0x9e3779b9

    def __hash__(self):
        return self.hash

    def __call__(self, obj, notFound = None):
        if obj is None:
            return None

        if self not in obj:
            return notFound
        return obj[self]

    def __repr__(self):
        return ":" + str(self.sym)

def keyword(*args):
    if len(args) == 1:
        if isinstance(args[0], Symbol):
            sym = args[0]
            if sym.meta() is not None:
                sym = sym.withMeta(None)
            k = Keyword(sym)

            interned.mutate(lambda old: old if sym in old else old.assoc(sym,k))

            return interned.get()[sym]
        elif isinstance(args[0], (str, unicode)):
            return keyword(symbol(args[0]))
        else:
            raise InvalidArgumentException()
    elif len(args) == 2:
        return keyword(symbol(*args))
    else:
        raise ArityException()

def find(self, *args):
    if len(args) == 1:
        if isinstance(args[0], Symbol):
            return interned.val()[args[0]]()
        if isinstance(args[0], str):
            return Keyword.find(symbol(args[0]))
    if len(args) == 2:
        return Keyword.find(symbol(*args))
    raise ArityException()


LINE_KEY = keyword(None, "line")
TAG_KEY = keyword(None, "tag")
T = keyword(None, "T")
