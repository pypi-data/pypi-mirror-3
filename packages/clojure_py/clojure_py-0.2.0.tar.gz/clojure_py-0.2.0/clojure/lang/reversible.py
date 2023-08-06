from clojure.lang.cljexceptions import AbstractMethodCall


class Reversible(object):
    def rseq(self):
        raise AbstractMethodCall(self)
