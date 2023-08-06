import functools

import pickle


class Curry(object):

    @staticmethod
    def curryFromPartialObject(partial):
        args = partial.args or ()
        kwds = partial.keywords or {}
        return Curry(partial.func, *args, **kwds)

    def __init__(self, function, *args, **kwds):
        self.initPartialObject(function, *args, **kwds)
        return

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, self.__class__):
            return False

        selfPartial = self._partial
        otherPartial = other._partial
        if selfPartial.func is not otherPartial.func:
            return False
        if not selfPartial.args == otherPartial.args:
            return False
        if not selfPartial.keywords == otherPartial.keywords:
            return False
        return True


    def __call__(self, *args, **kwds):
        return self._partial(*args, **kwds)

    def initPartialObject(self, function, *args, **kwds):
        self._partial = functools.partial(function,
                                          *args,
                                          **kwds)
        return

    def __getstate__(self):
        odict = self.__dict__.copy()
        
        odict['function'] = pickle.dumps(self._partial.func)
        odict['args'] = self._partial.args
        odict['keywords'] = self._partial.keywords
        del odict['_partial']
        return odict


    def __setstate__(self, dict):

        function = pickle.loads(dict['function'])
        args = dict['args']
        keywords = dict['keywords']

        self.initPartialObject(function, *args, **keywords)

        return

    # END class Curry
    pass
