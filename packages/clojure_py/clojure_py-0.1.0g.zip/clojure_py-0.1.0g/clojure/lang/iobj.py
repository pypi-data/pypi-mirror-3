from clojure.lang.cljexceptions import AbstractMethodCall

class IObj:
    def withMeta(self, meta):
        raise AbstractMethodCall(self)
