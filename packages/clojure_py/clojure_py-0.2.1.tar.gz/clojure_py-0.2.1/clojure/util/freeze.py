## A clojure-py implementation of deep-freeze. Used by the compiler
## for saving code modules
from clojure.lang.protocol import ProtocolFn
from clojure.lang.multimethod import MultiMethod
from clojure.lang.pytypes import *

topID = 0
seenID = topID
codeFreezeID = 1

def registerType(name):
    global topID
    topID += 1
    name = name + "ID"
    globals()["name"] = topID
    
    def identity(fn):
        return fn
        
    return identity
    
writeDispatcher = ProtocolFn("freeze-write")
read = MultiMethod(lambda id, *args: id)


_codeAttrs = filter(lambda x: not x.startswith("_"), dir(pyTypeCode))

def writeCode(code, strm, state):
    strm.write(codeFreezeID)
    
    for attr in _codeAttrs:
        write(getattr(code, attr), strm, state) 
        
writeDispatcher.extend(pyTypeCode, writeCode)


def write(obj, strm, state = None):
    if state is None:
        state = WriterState()
    
    if state.hasSeen(obj):
        strm.write(seenID)
        strm.write(state.getID(obj))
    
    writeDispatcher(obj, strm, state)
    
        

class WriterState(object):
    def __init__(self):
        self.seen = {}
        self.nextIDX = -1
        
    def hasSeen(self, obj):
        return obj in self.seen
        
    def getID(self, obj):
        return self.seen[obj]
        
    def markSeen(self, obj):
        self.nextIDX += 1
        self.seen[obj] = self.nextIDX
        



