import copy

#import peak.events
#from peak.events import trellis
import mext.reaction.collections as trellis

import currypy

import pypatterns.filter as FilterModule

class Table(object):
    
    JOIN_CROSS = 'cross join'
    JOIN_INNER = 'inner join'
    JOIN_LEFT = 'left join'
    JOIN_RIGHT = 'right join'
    JOIN_FULL = 'full join'

    NULL = object()

    COLUMN_ATTRIBUTE_UNIQUE = 'unique'

    
    @staticmethod
    def reduceRetrieve(table, filter, columns, initialValue=None):
        if initialValue is None:
            initialValue = []
        return reduce(lambda x, y: x+y,
                      table.retrieve(filter, columns),
                      initialValue)
    
    
    def __init__(self, name=None):
        self.name(name)
        self.rows(trellis.List([]))
        
        # columns defaults to a set
        # where the keys are the names of the columns
        # and the values are the attributes
        self.columns(trellis.Dict(**{}))
        
        return

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict['_rows'] = list(odict['_rows'])
        odict['_columns'] = dict(
            (key, set(value)) 
            for key, value in odict['_columns'].iteritems())
        return odict

    def __setstate__(self, odict):
        self.rows(trellis.List(odict['_rows']))
        d = dict((key, trellis.Set(value))
                 for key, value in odict['_columns'].iteritems())
        self.columns(trellis.Dict(**d))
        return
    
    def __eq__(self, other):
        for difference in self.getDifferencesWith(other):
            return False
        return True

    def __deepcopy__(self, memo):
        if self in memo:
            return memo[self]
        
        result = createTable(self.name(),
                             self.columns())
        for row in self.rows():
            newRow = result.addRow()
            for column in self.columns():
                columnValue = row.getColumn(column)
                columnValueCopy = copy.deepcopy(columnValue, memo)
                newRow.setColumn(column, columnValueCopy)
                
        memo[self] = result
        
        return result
    
    
    def getDifferencesWith(self, other):
        if not type(self) is type(other):
            yield 'not the same type'
        if not self.name() == other.name():
            yield 'self is named %s, but other is named %s' % (self.name(), other.name())
        if not set(self.columns()) == set(other.columns()):
            yield 'self has columns %s, but other has columns %s' % (self.columns(), other.columns())
        if not len(self.rows()) == len(other.rows()):
            yield 'self has %s rows, other has %s rows' % (len(self.rows()), len(other.rows()))
            
        # to optimize, lets sort both 
        columnComparatorMap = dict([(x, cmp) for x in self.columns()])
        rowComparator = currypy.Curry(Row.comparator,
                                          columnComparatorMap=columnComparatorMap)
        leftRows = sorted(self.rows(), rowComparator)
        rightRows = sorted(other.rows(), rowComparator)
        for leftRow, rightRow in zip(leftRows, rightRows):
            if rowComparator(leftRow, rightRow) is not 0:
                yield 'self has row %s, other has row %s' % (leftRow._values, rightRow._values)
                break
            pass
        
        raise StopIteration
    

    def name(self, value=None):
        if value is not None:
            self._name = value
        if not hasattr(self, '_name'):
            self._name = None
        return self._name

    def rows(self, value=None):
        if value is not None:
            self._rows = value
        if not hasattr(self, '_rows'):
            self._rows = None
        return self._rows

    def columns(self, value=None):
        if value is not None:
            self._columns = value
        if not hasattr(self, '_columns'):
            self._columns = None
        return self._columns

    
    def rowCount(self):
        return len(self.rows())
    
    def hasColumn(self, column):
        return column in self.columns()
    
    def addColumn(self, column):
        self.columns()[column] = trellis.Set([])
        return
    
    def addColumnAttribute(self, column, attribute):
        if not self.hasColumn(column):
            raise KeyError('table does not have column %s' % column)
        
        self.columns()[column].add(attribute)
        return
    
    
    def addRow(self, row=None):
        if row is None:
            row = Row(self)
        self.rows().append(row)
        return row


    def clear(self):
        filter = FilterModule.TRUE_FILTER
        return self.removeRows(filter)

    
    def removeRows(self, filter):
        rowsToRemove = [x for x in filter.wrap(self.rows())]
        map(self.rows().remove, rowsToRemove)
        return rowsToRemove

    
    def retrieve(self, filter=None, columns=None):
        if filter is None:
            filter = FilterModule.TRUE_FILTER
            
        if columns is None:
            columns = self.columns()
        
        for row in filter.wrap(self.rows()):
            rowValues = [row.getColumn(column) for column in columns]
            yield rowValues
            
        raise StopIteration

    
    def retrieveForModification(self, filter):
        for row in filter.wrap(self.rows()):
            yield row
            
        raise StopIteration
    
    
    def hasRow(self, filter):
        for row in filter.wrap(self.rows()):
            return True
        return False

    def update(self, other):
        if not set(self.columns.keys()).issuperset(other.columns().keys()):
            raise NotImplementedError
        otherColumns = other.columns().keys()
        for rowValues in other.retrieve(FilterModule.TRUE_FILTER, otherColumns):
            row = self.addRow()
            map(row.setValue, otherColumns, rowValues)
            pass
        return

    def addObjectAsRow(self, objectToAdd, objectKeyFunctionsMap):
        row = self.addRow()
        for column in self.columns():
            objectKeyFunction = objectKeyFunctionsMap[column]
            row.setColumn(column, objectKeyFunction(objectToAdd))
            pass
        return
    
    
    # END class Table
    pass

class Row(object):

    @staticmethod
    def comparator(left, right, columnComparatorMap):
        for column, comparator in columnComparatorMap.iteritems():
            compareValue = comparator(left.getColumn(column),
                                      right.getColumn(column))
            if not compareValue is 0:
                return compareValue
            pass
        return 0
    
    def __init__(self, table=None):
        
        self.table(table)

        self.values(trellis.Dict(**{}))
        
        return

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict['_values'] = dict(odict['_values'])
        return odict
    
    def __setstate__(self, odict):
        self.table(odict['_table'])
        d = odict['_values']
        values = trellis.Dict(**d)
        self.values(values)
        return    
    
    def values(self, value=None):
        if value is not None:
            self._values = value
        if not hasattr(self, '_values'):
            self._values = None
        return self._values

    def table(self, value=None):
        if value is not None:
            self._table = value
        if not hasattr(self, '_table'):
            self._table = None
        return self._table

    def hasColumn(self, column):
        return self.table().hasColumn(column)
    
    def setColumn(self, column, value):
        if not self.hasColumn(column):
            raise KeyError('row does not have column %s' % column)

        self.values()[column] = value
        return

    
    def getColumn(self, column):
        return self.values().get(column, Table.NULL)
    
    # END class Row
    pass

class ColumnValueFilter(FilterModule.ObjectFilter):
    
    """
    This is a filter on a row,
    and returns true if the value of the column in the row matches
    """
    
    def __init__(self, column, valueFilter):
        FilterModule.ObjectFilter.__init__(self,
            valueFunction = lambda: valueFilter,
            objectFunction = lambda x: x.getColumn(column),
            compareFunction = lambda x, y: y.matches(x)
        )
        self._column = column
        self._valueFilter = valueFilter
        
        return
    
    # END ColumnValueFilter
    pass


class ColumnJoinFilter(FilterModule.ObjectFilter):
    
    def __init__(self, left, right):
        FilterModule.ObjectFilter.__init__(
            self,
            valueFunction = lambda: True,
            objectFunction = lambda x: x[0].getColumn(self._left) == x[1].getColumn(self._right)
        )
        self._left = left
        self._right = right
        return
    
    # END JoinFilter
    pass


class JoinFilter(FilterModule.CompositeFilter):
    """
    This class defines the default/basic join filter
    that is used as the industry standard
    """
    
    def __init__(self, columnMap):
        FilterModule.CompositeFilter.__init__(
            self, FilterModule.AndAccumulator())
        
        map(self.addFilter, [ColumnJoinFilter(x, y) for x,y in columnMap.iteritems()])
        
        return
    
    # END class JoinFilter
    pass


def createTable(name, columns):
    table = Table(name=name)
    map(table.addColumn, columns)

    return table


def join(joinInfo):
    # left, right, aFilter, anOperator, joinType=None):
    """
    @param aFilter determines whether the rows should be joined
    @param anOperator does the actual joining
    """

    left = joinInfo['left']
    right = joinInfo['right']
    theFilter = joinInfo['filter']
    theOperator = joinInfo['operator']
    leftColumns = joinInfo['left columns']
    rightColumns = joinInfo['right columns']
    name = joinInfo['name']
    joinType = joinInfo['join type']
    
    
    # currently implementing in a code clean fashion
    # but should attempt to optimize instead
    # leftRows and otherRows will keep track of the unmatched rows
    leftRows = set(left.rows())
    rightRows = set(right.rows())
    joinedTable = createTable(name, leftColumns.values()+rightColumns.values())
    for leftRow in left.rows():
        for rightRow in right.rows():
            if not theFilter.matches((leftRow, rightRow)):
                continue
            
            leftRows.discard(leftRow)
            rightRows.discard(rightRow)
            
            theOperator(joinedTable, leftRow, rightRow)
            pass
        pass
    
    if joinType in [Table.JOIN_FULL, Table.JOIN_LEFT]:
        for row in leftRows:
            theOperator(joinedTable, leftRow, None)
        pass
    
    if joinType in [Table.JOIN_FULL, Table.JOIN_RIGHT]:
        for row in rightRows:
            theOperator(joinedTable, None, rightRow)
        pass
            
    return joinedTable


def defaultJoinOperator(table, left, right, leftColumnMap, rightColumnMap):
    row = table.addRow()
    
    # if not left, then we are doing a right join
    for sourceColumn, targetColumn in leftColumnMap.iteritems():
        valueToSet = Table.NULL
        if left:
            valueToSet = left.getColumn(sourceColumn)
        row.setColumn(targetColumn, valueToSet)
        pass

    for sourceColumn, targetColumn in rightColumnMap.iteritems():
        valueToSet = Table.NULL
        if right:
            valueToSet = right.getColumn(sourceColumn)
        row.setColumn(targetColumn, valueToSet)
        pass
    return
    
