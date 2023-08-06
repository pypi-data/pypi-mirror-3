"""
March 25, 2012 -- documented
"""

from clojure.lang.iobj import IObj
from clojure.lang.cljexceptions import AbstractMethodCall


class Obj(IObj, object):
    """An object that may have meta data attached.

    _meta -- a PersistentHashMap
             This attribute may not exist if a map has not been assigned.

    This map does not change the identiy of the object. When two subclass
    instances are compared, their meta data should be disregarded."""
    def meta(self):
        """Return a PersistentHashMap or None if no meta data attached."""
        if not hasattr(self, "_meta"):
            return None
        return self._meta

    def withMeta(self, meta):
        """Attach meta data to a subclass instance.

        meta -- a PersistentHashMap

        Subclasses generally return a *new* instance of themselves with meta
        attached.

        This base raises AbstractMethodCall"""
        raise AbstractMethodCall(self)
