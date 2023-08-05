import currypy
import logging


def FUNCTION_IDENTITY(object=None):
    return object

FUNCTION_TRUE = currypy.Curry(FUNCTION_IDENTITY, object=True)
FUNCTION_FALSE = currypy.Curry(FUNCTION_IDENTITY, object=False)


def FUNCTION_IDENTITY_2(x, y):
    return x is y

def FUNCTION_EQUIVALENCE_2(x, y):
    return x == y

class Filter(object):

    def __init__(self):
        self._matched = set([])
        self._notMatched = set([])
        self._shouldCache = True
        return
    
    def __repr__(self):
        return self.name()

    def name(self, value=None):
        if value is not None:
            self._name = value
        if not hasattr(self, '_name'):
            self._name = '%s' % self.__class__
        return self._name


    def wrap(self, iterable, objectFunction=FUNCTION_IDENTITY):
        """
        this will wrap a filter around a generator/iterator 
        so that the new generator returns only values
        produced by the previous generator, but filtered
        by the filter provided
        aFunction also allows for specifying 
        if some attribute should be returned 
        instead of the object instead 
        """
        for x in iterable:
            if self.matches(x):
                theObject = objectFunction(x)
                yield theObject
                pass
            pass
        pass

    def hasMatched(self, object):
        if isinstance(object, list):
            object = tuple(object)
        if isinstance(object, dict):
            return False
        return object in self._matched
    
    def hasNotMatched(self, object):
        if isinstance(object, list):
            object = tuple(object)
        if isinstance(object, dict):
            return False
        return object in self._notMatched
    
    def addMatched(self, object):
        if isinstance(object, list):
            object = tuple(object)
        if isinstance(object, dict):
            return
        self._matched.add(object)
        return
    
    def addNotMatched(self, object):
        if isinstance(object, list):
            object = tuple(object)
        if isinstance(object, dict):
            return
        self._notMatched.add(object)
        return

    def resetCachedMatches(self):
        self._matched = set([])
        self._notMatched = set([])
        return

    
    def clearCacheofObject(self, object):
        self._matched.discard(object)
        self._notMatched.discard(object)
        pass
    
    
    def matches(self, object):
        raise NotImplementedError

    pass

class ObjectFilter(Filter):
    def __init__(self, 
                 valueFunction, 
                 objectFunction=None,
                 compareFunction=None):
        
        Filter.__init__(self)
        
        self.expected = valueFunction

        # default the actual value to object being passed in
        if objectFunction is None:
            objectFunction = FUNCTION_IDENTITY
        self._objectFunction = objectFunction

        # default comparator to identity comparison
        if compareFunction is None:
            compareFunction = FUNCTION_IDENTITY_2
        self._compareFunction = compareFunction

        pass

    def actual(self, object):
        """
        give an object, retrieves the actual value to be compared
        """
        return self._objectFunction(object)

    def matches(self, object):

        if self._shouldCache:
            if self.hasMatched(object):
                return True
            if self.hasNotMatched(object):
                return False
            pass
        
        try:
            actualValue = self.actual(object)
            expectedValue = self.expected()
            compareValue = self._compareFunction(actualValue, expectedValue)
            if compareValue:
                self.addMatched(object)
            else:
                self.addNotMatched(object)
            return compareValue
        except Exception, e:
            logging.error('something is wrong, filter got exception "%s", returning False' % e)
            self.addNotMatched(object)
            return False

    # END class ObjectFilter
    pass


def FUNCTION_TRUE_1(x):
    return True

def FUNCTION_FALSE_1(x):
    return False

TRUE_FILTER = ObjectFilter(valueFunction=FUNCTION_TRUE,
                           objectFunction=FUNCTION_TRUE_1)
TRUE_FILTER.name('TrueFilter')
TRUE_FILTER._shouldCache = False

FALSE_FILTER = ObjectFilter(valueFunction=FUNCTION_FALSE,
                            objectFunction=FUNCTION_TRUE_1)
FALSE_FILTER.name('FalseFilter')
FALSE_FILTER._shouldCache = False


class ObjectKeyMatchesFilter(ObjectFilter):

    @staticmethod
    def match(objectToMatch, filterObject):
        
        if not filterObject._hasKeyFunction(objectToMatch):
            return False
        
        try:
            keyToMatch = filterObject._keyFunction(objectToMatch)
            return filterObject._filter.matches(keyToMatch)
        except Exception, e:
            logging.error('could not retrieve key >> %s' % e)
            pass
        return False

    @staticmethod
    def defaultHasKeyFunction(x):
        return True
    
    def __init__(self, filter=None, keyFunction=None, hasKeyFunction=None):
        ObjectFilter.__init__(
            self,
            valueFunction = FUNCTION_TRUE,
            objectFunction = lambda x: ObjectKeyMatchesFilter.match(x, self)
        )
        self._filter = filter
        self._keyFunction = keyFunction
        if hasKeyFunction is None:
            hasKeyFunction = ObjectKeyMatchesFilter.defaultHasKeyFunction
        self._hasKeyFunction = hasKeyFunction
            
        return

    # END class ObjectKeyMatchesFilter
    pass


class MemberOfObjectKeyMatchesFilter(Filter):
    
    def __init__(self, accumulator=None, filter=None,
                 keyFunction=None, hasKeyFunction=None):
        
        Filter.__init__(self)

        self._accumulator = accumulator
        self._filter = filter
        self._keyFunction = keyFunction
        if hasKeyFunction is None:
            hasKeyFunction = ObjectKeyMatchesFilter.defaultHasKeyFunction
        self._hasKeyFunction = hasKeyFunction
        pass

    def accumulator(self):
        return self._accumulator
    
    
    def matches(self, object):

        if self._shouldCache:
            if self.hasMatched(object):
                return True
            if self.hasNotMatched(object):
                return False
            pass

        result = False
        if self._hasKeyFunction(object):
            
            try:
                filter = self._filter
                keyToMatch = self._keyFunction(object)
                accumulator = self.accumulator()
                accumulator.reset()
                for member in keyToMatch:
                    value = filter.matches(member)
                    accumulator.add(value)
                    if accumulator.isDone():
                        break
                    pass
                result = accumulator.value()
            except Exception, e:
                logging.error('could not retrieve key >> %s' % e)
                pass
            
            pass
        
        if result:
            self.addMatched(object)
        else:
            self.addNotMatched(object)
        return result
    
    
    # END MemberOfObjectKeyMatchesFilter
    pass


class IdentityFilter(ObjectFilter):
    def __init__(self, value):
        ObjectFilter.__init__(
            self,
            valueFunction = currypy.Curry(FUNCTION_IDENTITY,
                                              object=value),
            objectFunction = FUNCTION_IDENTITY)
        self.name('IdentityFilter(%s)' % str(value))
        return

    # END class IdentityFilter
    pass


class EquivalenceFilter(ObjectFilter):
    def __init__(self, value):
        ObjectFilter.__init__(
            self,
            valueFunction = currypy.Curry(FUNCTION_IDENTITY,
                                              object=value),
            objectFunction = FUNCTION_IDENTITY,
            #compareFunction = lambda x, y: x==y)
            compareFunction = FUNCTION_EQUIVALENCE_2
        )
        self.name('EquivalenceFilter(%s)' % value)
        return

    # END class EquivalenceFilter
    pass




class NameFilter(ObjectKeyMatchesFilter):
    @staticmethod
    def objectName(symbol):
        """
        given a symbol, return the
        string that represents the object's name
        """
        return symbol.name()
    
    def __init__(self, value):
        ObjectKeyMatchesFilter.__init__(
            self,
            EquivalenceFilter(value),
            NameFilter.objectName
        )
        self.name('NameFilter(%s)'%value)
        return

    # END class NameFilter
    pass


class IdFilter(ObjectKeyMatchesFilter):
    def __init__(self, value):
        ObjectKeyMatchesFilter.__init__(
            self,
            EquivalenceFilter(value),
            lambda x: x.id()
        )
        self.name('IdFilter(%s)'%value)
        return
    
    # END class IdFilter
    pass


class CompositeFilter(Filter):
    def __init__(self, accumulator):
        Filter.__init__(self)
        
        self.reset()
        self._accumulator = accumulator
        return


    def __repr__(self):
        return '%s:%s' % (self._accumulator, self.name())


    def reset(self):
        self._filters = []
        self.resetCachedMatches()
        pass
    
    def addFilter(self, filter):
        self._filters.append(filter)
        self.resetCachedMatches()
        return

    def removeFilter(self, filter):
        self._filters.remove(filter)
        self.resetCachedMatches()
        return

    
    def removeFilterUsingFilter(self, filter, recursive=False):
        theFilters = [x for x in self._filters]
        for theFilter in theFilters:
            if filter.matches(theFilter):
                #self._filters.remove(filter)
                self.removeFilter(filter)
                pass
            elif isinstance(theFilter, CompositeFilter) and recursive:
                theFilter.removeFilterUsingFilter(filter, recursive)
            pass
        return

    def accumulator(self):
        return self._accumulator

    def expected(self):
        expectedList = [filter.expected() for filter in self._filters]
        return "%s(%s)" % (self.accumulator(), expectedList)

    def actual(self, object):
        actualList = [filter.actual(object) for filter in self._filters]
        return "%s(%s)" % (self.accumulator(), actualList)

    def assertMatches(self, subfilter, object):
        return subfilter.matches(object)

    def matches(self, object):

        if self._shouldCache:
            if self.hasMatched(object):
                return True
            if self.hasNotMatched(object):
                return False
            pass
        
        accumulator = self.accumulator()
        accumulator.reset()
        for filter in self._filters:
            value = False
            try:
                value = self.assertMatches(filter, object)
            except Exception, e:
                pass
            accumulator.add(value)
            if accumulator.isDone():
                break
            pass

        result = accumulator.value()
        if result:
            self.addMatched(object)
        else:
            self.addNotMatched(object)
        return result
    

    # END class CompositeFilter
    pass

class Accumulator(object):
    def __init__(self):
        self.reset()
        return

    def reset(self):
        self._hasValue = False

    def add(self, value):
        raise NotImplementedError

    def isDone(self):
        return self._hasValue

    def value(self):
        return self._value

class AndOrAccumulator(Accumulator):
    """
    this accumulator will return true iff
    it is given [min,max] True values
    """
    def __init__(self, min=1, max=1):
        Accumulator.__init__(self)
        self._min = min
        self._max = max
        pass


    def reset(self):
        Accumulator.reset(self)
        self._count = 0
        self._value = False

    def add(self, value):
        if value is True:
            self._count = self._count + 1
        # has not gotten the necessary number of True
        if self._count < self._min:
            self._value = False
        # received more than max number of True
        elif self._count > self._max:
            self._value = False
            # value can no longer change anymore
            self._hasValue = True
        else:
            self._value = True
        return

class AndAccumulator(Accumulator):
    def __init__(self):
        Accumulator.__init__(self)
        return

    def __repr__(self):
        return "And"

    def reset(self):
        Accumulator.reset(self)
        self._value = True

    def add(self, value):
        self._value &= value
        if not self._value:
            self._hasValue = True

class OrAccumulator(Accumulator):
    def __init__(self):
        Accumulator.__init__(self)
        pass

    def __repr__(self):
        return "Or"

    def reset(self):
        Accumulator.reset(self)
        self._value = False

    def add(self, value):
        self._value |= value
        if self._value:
            self._hasValue = True

class NotAccumulator(Accumulator):
    def __init__(self):
        Accumulator.__init__(self)
        pass

    def __repr__(self):
        return "Not"

    def add(self, value):
        self._value = not value
        self._hasValue = True




def constructAndFilter():
    return CompositeFilter(AndAccumulator())

def constructOrFilter():
    return CompositeFilter(OrAccumulator())

def constructNotFilter():
    return CompositeFilter(NotAccumulator())

