from clojure.lang.areference import AReference
from clojure.lang.atomicreference import AtomicReference
from clojure.lang.persistenthashmap import EMPTY as EMPTY_MAP
from clojure.lang.cljexceptions import (InvalidArgumentException,
                                        IllegalStateException,
                                        ArityException,
                                        IllegalArgumentException)
import clojure.lang.rt as RT
from clojure.lang.symbol import Symbol, symbol
import sys, types

namespaces = AtomicReference(EMPTY_MAP)

def areDifferentInstancesOfSameClassName(o1, o2):
    return o1.__class__ is o2.__class__

def addDefaultImports(mod):
    import clojure.lang.rt as RT
    import clojure.standardimports as stdimps
    for i in dir(stdimps):
        if i.startswith("_"):
            continue
        setattr(mod, i, getattr(stdimps, i))
    if "clojure.core" in sys.modules:
        core = sys.modules["clojure.core"]
        for i in dir(core):
            if i.startswith("_"):
                continue
            setattr(mod, i, getattr(core, i))
    return mod

def findOrCreateIn(module, parts):
    if not parts:
        return module
    part = parts[0]
    parts = parts[1:]
    if hasattr(module, part):
        return findOrCreateIn(getattr(module, part), parts)
    mod = types.ModuleType(module.__name__ + "." + part)
    setattr(module, part, mod)
    return findOrCreateIn(mod, parts)
    


def findOrCreate(name):
    from clojure.lang.symbol import Symbol
    if isinstance(name, Symbol):
        name = name.name
    if name in sys.modules:
        return sys.modules[name]

    mod = types.ModuleType(name)
    sys.modules[name] = mod

    addDefaultImports(mod)
    return mod

def remove(name):

    if isinstance(name, types.ModuleType):
        name = name.__name__
    if isinstance(name, Symbol):
        name = name.name
    if name not in sys.modules:
        raise KeyError("module " + name + " not found")
    if name == "clojure.core":
        raise IllegalArgumentException("Cannot remove clojure namespace");
    del sys.modules[name]
    return None
            
    

def find(name, fromns = None):
    from clojure.lang.symbol import Symbol
    if isinstance(name, types.ModuleType):
        return name
    if isinstance(name, Symbol):
        name = name.name
    
    if not fromns is None:
        if hasattr(fromns, "__aliases__"):
            if fromns in fromns.__aliases__: 
                return fromns.__aliases__[name]
    return sys.modules[name]

def findItem(ns, sym):
    from clojure.lang.symbol import Symbol, symbol
    if sym.ns is not None and  hasattr(ns, "__aliases__") and \
        symbol(sym.ns) in ns.__aliases__:
        sym = symbol(ns.__aliases__[symbol(sym.ns)].__name__, sym.name)
       
    if isinstance(sym, Symbol):
        if ns is None:
            ns = sys.modules["clojure.core"] # we need this to boostrap files
        if sym.ns == ns.__name__:
            if not hasattr(ns, sym.name):
                return None
            return getattr(ns, sym.name)
        if sym.ns is not None:
            mod = find(sym.ns, ns)
            if hasattr(mod, sym.name):
                return getattr(mod, sym.name)
            return None
        if not hasattr(ns, str(sym)):
            return None
        return getattr(ns, str(sym))
    return getattr(ns, sym)

def findModule(sym, module = None):
    if module is None:
        sym = sym.split(".")
        parts = sym[1:]
        name = sym[0]
        if name not in sys.modules:
            return None
        if len(parts):
            return findModule(parts, sys.modules[name])
        return sys.modules[name]

    name = sym[0]
    parts = sym[1:]
    if not hasattr(module, name):
        return None
    if len(parts):
        return findModule(parts, getattr(module, name))
    return getattr(module, name)

def intern(ns, sym):
    from clojure.lang.var import Var


    if isinstance(sym, str):
        sym = symbol(str)

    if sym.ns is not None:
        raise InvalidArgumentException("Can't intern namespace-qualified symbol")

    ns = find(ns)
    if hasattr(ns, str(sym)):
        v = getattr(ns, str(sym))
        if not isinstance(v, Var):
            raise Exception("can't redefine " + str(v) + " as " + str(sym) + ": is not Var")
        if ns.__name__ == v.ns.__name__:
            return v
    v = Var(ns, sym)
    setattr(ns, sym.name, v)
    return v
    

