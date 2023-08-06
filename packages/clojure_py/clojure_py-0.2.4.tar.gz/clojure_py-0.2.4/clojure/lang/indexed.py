from clojure.lang.cljexceptions import AbstractMethodCall
from clojure.lang.counted import Counted

class Indexed(Counted, object):
    def nth(self, i, notFound = None):
        raise AbstractMethodCall(self)