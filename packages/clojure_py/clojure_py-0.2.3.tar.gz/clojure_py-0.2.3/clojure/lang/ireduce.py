from clojure.lang.cljexceptions import AbstractMethodCall

class IReduce(object):
    def reduce(self, *args):
        raise AbstractMethodCall(self)
