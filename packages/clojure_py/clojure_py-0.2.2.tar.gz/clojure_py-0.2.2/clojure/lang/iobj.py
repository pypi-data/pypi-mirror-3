from clojure.lang.cljexceptions import AbstractMethodCall

class IObj(object):
    def withMeta(self, meta):
        raise AbstractMethodCall(self)
