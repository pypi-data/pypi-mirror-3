from clojure.lang.cljkeyword import keyword

default = keyword("default")

class MultiMethodException(Exception):
    def __init__(self, reason):
        Exception.__init__(self, reason)

class MultiMethod(object):
    def __init__(self, selector):
        self.selector = selector
        self.fns = {}
        self.default = None
        
    def addMethod(self, value, fn):
        if value in self.fns:
            raise MultiMethodException("Method already exists for value " + str(value))
        if value == default and self.default is not none:
            raise MultiMethodException("Method already exists for value " + str(value))

        if value == default:
            self.default = fn
        else:
            self.fns[value]
            
    def __call__(self, *args):
        dval = self.selector(*args)
        
        try:
            fn = self.fns[dval]
        except KeyError:
            if not self.default:
                return self.default(*args)
            raise MultiMethodException("No match for dispatch value " + str(value))
        
        return fn(*args)

