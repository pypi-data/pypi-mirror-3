from clojure.lang.namespace import findOrCreate as findNamespace

class ProtocolException(Exception):
    pass
    # def __init__(self, msg):
    #     Exception__init__(msg)



def getFuncName(protocol, funcname):
    return str(protocol) + funcname
    
class ProtocolFn(object):
    """Defines a function that dispatches on the type of the first argument
    passed to __call__"""
    
    def __init__(self, fname):
        self.dispatchTable = {}
        self.name = intern(fname)
        self.attrname = intern("__proto__" + self.name)
        self.default = None
        
    def extend(self, tp, fn):
           
        try:
            setattr(tp, self.attrname, fn)
        except:
            self.dispatchTable[tp] = fn
            
    def extendForTypes(self, tps, fn):
        for tp in tps:
            self.extend(tp, fn)
            
    def setDefault(self, fn):
        self.default = fn
            
    def isExtendedBy(self, tp):
        if hasattr(tp, self.attrname) or tp in self.dispatchTable:
            return True
        return False
        
           
    def __call__(self, *args):
        x = type(args[0])
        if hasattr(x, self.attrname):
            return getattr(x, self.attrname)(*args)
        else:
            # The table needs to be checked before the fn is called.
            #
            # If the following is used:
            #
            # try:
            #     return self.dispatchTable[x](*args)
            # except
            #     if self.default:
            #         return self.default(*args)
            #     raise
            #
            # the dispatched fn may raise (even a KeyError). That exception
            # will get silently swallowed and the default fn will get called.
            # I believe the following will handle this, but it will also
            # affect performance.
            fn = self.dispatchTable.get(x)
            if fn:
                # let any fn exceptions propogate
                return fn(*args)
            else:
                # now try the default and raise a specific exception
                if self.default:
                    # let any default fn exceptions propogate
                    return self.default(*args)
                raise ProtocolException("{0} not extended to handle: {1}"
                                        .format(self.name, x))

            
    def __repr__(self):
        return "ProtocolFn<" + self.name + ">"
        
    
    
class Protocol(object):
    def __init__(self, ns, name, fns):
        """Defines a protocol in the given ns with the given name and functions"""
        self.ns = ns
        self.name = name
        self.fns = fns
        self.protofns = registerFns(ns, fns)
        self.__name__ = name
        self.implementors = {}
        
    def markImplementor(self, tp):
        if tp.__name__ in self.implementors:
            return
            
        self.implementors[tp.__name__] = tp
        
    def extendForType(self, tp, mp):
        """Extends this protocol for the given type and the given map of methods
           mp should be a map of methodnames: functions"""
       
        for x in mp:
            name =  RT.name(x.sym)
            if name not in self.protofns:
                raise ProtocolException("No Method found for name " + x)
            
            fn = self.protofns[name]
            fn.extend(tp, mp[x])
                
       
        
    def __repr__(self):
        return "Protocol<" + self.name + ">"
        
        
        
def registerFns(ns, fns):
    ns = findNamespace(ns)
    protofns = {}
    for fn in fns:
        fname = ns.__name__ + fn
        if hasattr(ns, fn):
            proto = getattr(ns, fn)
        else:
            proto = ProtocolFn(fname)
            setattr(ns, fn, proto)
        proto.__name__ = fn
        protofns[fn] = proto
        
    return protofns
    
def extend(np, *args):
    for x in range(0, len(args), 2):
        tp = args[x]
        proto = getExactProtocol(tp)
        if not proto:
            raise ProtocolExeception("Expected protocol, got " + str(x))
        if x + 1 >= len(args):
            raise ProtocolExeception("Expected even number of forms to extend")
        
        proto.extendForType(np, args[x + 1])
        
                
        
        
def getExactProtocol(tp):
    if hasattr(tp, "__exactprotocol__") \
       and hasattr(tp, "__exactprotocolclass__") \
       and tp.__exactprotocolclass__ is tp:
           return tp.__exactprotocol__
    return None
        
def protocolFromType(ns, tp):
    """Considers the input type to be a prototype for a protocol. Useful for
    turning abstract classes into protocols"""
    fns = []    
    for x in dir(tp):
        if not x.startswith("_"):
            fns.append(x)
            

        
    thens = findNamespace(ns)
    proto = Protocol(ns, tp.__name__, fns)
    
    tp.__exactprotocol__ = proto
    tp.__exactprotocolclass__ = tp
    
    if not hasattr(tp, "__protocols__"):
        tp.__protocols__ = []
    tp.__protocols__.append(proto)
    
    if not hasattr(thens, tp.__name__):
        setattr(thens, tp.__name__, proto)
    return proto
    
def extendForAllSubclasses(tp):
    if not hasattr(tp, "__protocols__"):
        return
    
    for proto in tp.__protocols__:
        _extendProtocolForAllSubclasses(proto, tp)
        
def _extendProtocolForAllSubclasses(proto, tp):
    extendProtocolForClass(proto, tp)
    
    for x in tp.__subclasses__():
        _extendProtocolForAllSubclasses(proto, x)
    

def extendForType(interface, tp):
    if not hasattr(interface, "__protocols__"):
        return
    
    for proto in interface.__protocols__:
        extendProtocolForClass(proto, tp)

def extendProtocolForClass(proto, tp):
    for fn in proto.protofns:
        
        pfn = proto.protofns[fn]
        if hasattr(tp, fn):
            pfn.extend(tp, getattr(tp, fn))
        
    proto.markImplementor(tp)
    
        
# Fixup globals
import clojure.lang.rt as RT
    
    
    
        
