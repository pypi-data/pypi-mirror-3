from clojure.lang.cljexceptions import AbstractMethodCall

class Iterable(object):
    def __iter__(self):
        raise AbstractMethodCall(self)
