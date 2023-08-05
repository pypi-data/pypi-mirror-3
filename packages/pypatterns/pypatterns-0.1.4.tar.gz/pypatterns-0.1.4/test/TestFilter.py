import os
import sys
import unittest
import logging

APP_ROOT = os.getenv('APP_ROOT')

sys.path.insert(0, '%s/currypy/src' % APP_ROOT)
sys.path.insert(0, '%s/pypatterns/src' % APP_ROOT)

import pypatterns.filter as FilterModule

class Resource(object):

    def name(self, value=None):
        if value is not None:
            self._name = value
        if not hasattr(self, '_name'):
            self._name = None
        return self._name
    
    # END class
    pass

class TestCase(unittest.TestCase):

    def testNotFilter(self):
        name = "test"

        # create the filter
        aFilter = FilterModule.constructNotFilter()
        aFilter.addFilter(FilterModule.NameFilter(name))

        aResource = Resource()
        aResource.name(name)
        assert aFilter.matches(aResource) is False, \
            "expected notfilter to not match resource named %s" % aResource.name()
        
        name = "wrong name"
        aResource = Resource()
        aResource.name(name)
        assert aFilter.matches(aResource), \
            "expected notfilter to match resource named %s" % aResource.name()

        pass

    def testAndOrFilter(self):
        name1 = "test1"
        name2 = "test2"

        resource1 = Resource()
        resource1.name(name1)
        resource2 = Resource()
        resource2.name(name2)

        # test to make sure that if min passes, succeeds
        aFilter = FilterModule.CompositeFilter(FilterModule.AndOrAccumulator())
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))
        assert aFilter.matches(resource1) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource1.name()
        assert aFilter.matches(resource2), \
            "expected andor(1,1) filter to accept resource %s" %resource2.name()

        # test to make sure that if max passes, succeeds
        aFilter = FilterModule.CompositeFilter(FilterModule.AndOrAccumulator(2,2))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))
        assert aFilter.matches(resource1), \
            "expected andor(1,1) filter to accept resource %s" % resource1.name()
        assert aFilter.matches(resource2) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource2.name()

        # test to make sure that if too many Filters passes, fails
        aFilter = FilterModule.CompositeFilter(FilterModule.AndOrAccumulator(0,0))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))
        assert aFilter.matches(resource1) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource1.name()
        assert aFilter.matches(resource2) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource2.name()        

        # test to make sure that if not enough Filters pass, fails
        aFilter = FilterModule.CompositeFilter(FilterModule.AndOrAccumulator(3,3))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))
        assert aFilter.matches(resource1) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource1.name()
        assert aFilter.matches(resource2) is False, \
            "expected andor(1,1) filter to not accept resource %s" % resource2.name()        

        pass

    def testOrFilter(self):
        name1 = "test1"
        name2 = "test2"
        name3 = "test3"

        aFilter = FilterModule.constructOrFilter()
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))

        # if any passes, succeed
        aResource = Resource()
        aResource.name(name1)
        assert aFilter.matches(aResource), \
            "expected orfilter to match resource named %s" % aResource.name()

        aResource = Resource()
        aResource.name(name2)
        assert aFilter.matches(aResource), \
            "expected orfilter to match resource named %s" % aResource.name()

        aResource = Resource()
        aResource.name(name3)
        assert not aFilter.matches(aResource), \
            "expected orfilter to match resource named %s" % aResource.name()

        # run again
        aResource = Resource()
        aResource.name(name1)
        assert aFilter.matches(aResource), \
            "expected notfilter to match resource named %s" % aResource.name()
        aResource = Resource()
        aResource.name(name2)
        assert aFilter.matches(aResource), \
            "expected notfilter to match resource named %s" % aResource.name()
        aResource = Resource()
        aResource.name(name3)
        assert not aFilter.matches(aResource), \
            "expected notfilter to match resource named %s" % aResource.name()
        

    def testAndFilter(self):
        name1 = "test1"
        name2 = "test2"

        aFilter = FilterModule.constructAndFilter()
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name1))

        # if all passes, succeed
        aResource = Resource()
        aResource.name(name1)
        assert aFilter.matches(aResource), \
            "expected andfilter to match resource named %s" % aResource.name()

        # if none passes, fail
        aResource = Resource()
        aResource.name(name2)
        assert aFilter.matches(aResource) is False, \
            "expected andfilter to not match resource named %s" % aResource.name()

        # if only some passes, fail
        aFilter = FilterModule.constructAndFilter()
        aFilter.addFilter(FilterModule.NameFilter(name1))
        aFilter.addFilter(FilterModule.NameFilter(name2))
        aResource = Resource()
        aResource.name(name1)
        assert aFilter.matches(aResource) is False, \
            "expected andfilter to not match resource named %s" % aResource.name()

        pass

    def testOrFilter(self):
        pass

    def testObjectFilter(self):
        pass

    def testNameFilter(self):

        name = "test"

        aFilter = FilterModule.NameFilter(name)

        aResource = Resource()
        aResource.name(name)
        assert aFilter.matches(aResource), \
            "expected filter to match resource named %s" % aResource.name()

        aResource = Resource()
        aResource.name("wrong name")
        assert aFilter.matches(aResource) is False, \
            "expected filter to not match resource named %s" % aResource.name()

        pass

    def testGeneratorFilter(self):
        """
        this test the ability to apply a filter to values
        produced by an iterator and/or generator
        """
        lists = []
        functions = []

        numbers = range(1,11)

        lists.append(numbers)
        functions.append(lambda x: x)

        lists.append([(0,x) for x in numbers])
        functions.append(lambda x: x[1])

        for list, function in zip(lists, functions):

            mod2Filter = FilterModule.ObjectFilter(lambda: 0,
                                             lambda x: function(x) % 2)
            mod2Filtered = mod2Filter.wrap(list)

            mod5Filter = FilterModule.ObjectFilter(lambda: 0,
                                             lambda x: function(x) % 5)
            
            filtered = mod5Filter.wrap(mod2Filtered, 
                                       objectFunction=function)
            
            cardinality = 0
            for number in filtered:
                if cardinality > 0:
                    assert False, \
                        "expected only one value in generator"
                assert number is 10, \
                    "expected value to be 10, got %s" % number
                cardinality = cardinality + 1
                pass
        pass


    def testMemberOfObjectKeyMatchesFilter1(self):
        
        filter = FilterModule.MemberOfObjectKeyMatchesFilter(
            filter = FilterModule.IdentityFilter(2),
            accumulator = FilterModule.AndAccumulator(),
            keyFunction = lambda x: x.values()         
        )
        filter._shouldCache = False
        
        class X(object):
            pass
        
        obj = X()
        setattr(obj, 'values', lambda: [0, 2, 2])
        assert not filter.matches(obj)
        
        setattr(obj, 'values', lambda: [2, 2, 2])
        assert filter.matches(obj)
        
        return
    
    def testMemberOfObjectKeyMatchesFilter2(self):
        
        filter = FilterModule.MemberOfObjectKeyMatchesFilter(
            filter = FilterModule.IdentityFilter(2),
            accumulator = FilterModule.OrAccumulator(),
            keyFunction = lambda x: x.values()         
        )
        filter._shouldCache = False
        
        class X(object):
            pass
        
        obj = X()
        setattr(obj, 'values', lambda: [0, 2, 1])
        assert filter.matches(obj)
        
        setattr(obj, 'values', lambda: [0, 1, 3])
        assert not filter.matches(obj)
        
        return
    
    
    pass

def main():
    suite = unittest.makeSuite(TestCase,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

