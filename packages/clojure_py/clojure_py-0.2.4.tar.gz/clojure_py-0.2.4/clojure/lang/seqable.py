from clojure.lang.cljexceptions import AbstractMethodCall


class Seqable(object):
    def seq(self):
        raise AbstractMethodCall(self)
