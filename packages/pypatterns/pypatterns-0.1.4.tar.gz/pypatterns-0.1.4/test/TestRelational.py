import os
import sys
import unittest
import logging

APP_ROOT = os.getenv('APP_ROOT')

sys.path.insert(0, '%s/currypy/src' % APP_ROOT)
import currypy

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

sys.path.insert(0,"../data")

class TestCase(unittest.TestCase):

    COLUMNS = ['column1', 'column2', 'column3']
    
    
    def testTable(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test',columns)
        
        rowValuesList = [
            [1,2,3],
            [1,'2','3'],
            [None,None,[]]
        ]
        for rowValues in rowValuesList:
            row = table.addRow()
            map(row.setColumn, columns, rowValues)

        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1',
            FilterModule.ObjectFilter(
                valueFunction=lambda: 1,
                objectFunction=lambda x: x)
            )
        
        for actualValues, expectedValues in \
            zip(table.retrieve(columnValueFilter, columns[1:]), rowValuesList):
            
            assert actualValues == expectedValues[1:]
            
            
        return
    
    def testRow(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test',columns)
        
        expectedValues = [1,2,3]
        row1 = table.addRow()
        map(row1.setColumn, columns, expectedValues)
        for column, expectedValue in zip(columns, expectedValues):
            assert row1.getColumn(column) == expectedValue
            pass
        
        expectedValues = [RelationalModule.Table.NULL, 'foo', 'bar']
        row2 = table.addRow()
        map(row2.setColumn, columns[1:], expectedValues[1:])
        for column, expectedValue in zip(columns, expectedValues):
            assert row2.getColumn(column) == expectedValue
            pass
        
        return

    
    def testColumnValueFilter(self):
        table = self.buildDefaultTable()

        columns = TestCase.COLUMNS
        row = table.rows()[0]
        rowValues = [1, '1', None]

        for column, rowValue in zip(columns, rowValues):
            valueFilter = FilterModule.IdentityFilter(rowValue)
            columnValueFilter = RelationalModule.ColumnValueFilter(column, valueFilter)
            assert columnValueFilter.matches(row)

        return

    
    def testRemoveRows(self):
        table = self.buildDefaultTable()

        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1', FilterModule.IdentityFilter(1))
        
        table.removeRows(columnValueFilter)

        assert len(table.rows()) is 0
        
    
    def testModifyRow(self):
        table = self.buildDefaultTable()

        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1', FilterModule.IdentityFilter(1))
        for row in table.retrieveForModification(columnValueFilter):
            row.setColumn('column1', 2)
            
        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1', FilterModule.IdentityFilter(2))
        for rowValues in table.retrieve(columnValueFilter, ['column1']):
            assert rowValues[0] is 2
        
        return
    

    def buildDefaultTable(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test', columns)

        row = table.addRow()
        rowValues = [1, '1', None]
        map(row.setColumn, columns, rowValues)
        
        return table

    
    def testJoins(self):
        
        employeeTable = getEmployeeTable()
        departmentTable = getDepartmentTable()
        
        leftColumns = {'surname':'surname'}
        rightColumns = {
            'id':'department id',
            'name':'department name'
        }
        theFilter = RelationalModule.JoinFilter(
            {'department id':'id'}
        )
        theOperator = currypy.Curry(
            RelationalModule.defaultJoinOperator,
            leftColumnMap = leftColumns,
            rightColumnMap = rightColumns
        )
        joinInfo = {
            'left':employeeTable,
            'right':departmentTable,
            'filter':theFilter,
            'operator':theOperator,
            'left columns':leftColumns,
            'right columns':rightColumns,
            'name':'join',
        }
        
        
        for joinType, expectedResults in [
            (RelationalModule.Table.JOIN_INNER, getExpectedInnerJoinResults()),
            (RelationalModule.Table.JOIN_LEFT, getExpectedLeftJoinResults()),
            (RelationalModule.Table.JOIN_RIGHT, getExpectedRightJoinResults()),
            (RelationalModule.Table.JOIN_FULL, getExpectedFullJoinResults())]:
        
            joinInfo['join type']  = joinType
        
            actualResult = RelationalModule.join(joinInfo)

            assert expectedResults == actualResult
        return
    
    
    # END class TestCase
    pass


def getExpectedInnerJoinResults():
    expectedResults = RelationalModule.createTable(
        'join', ['surname', 'department id', 'department name'])
    for surname, id, name in [('Smith', 34, 'Clerical'),
                              ('Jones', 33, 'Engineering'),
                              ('Robinson', 34, 'Clerical'),
                              ('Steinberg', 33, 'Engineering'),
                              ('Rafferty', 31, 'Sales')]:
        row = expectedResults.addRow()
        row.setColumn('surname', surname)
        row.setColumn('department id', id)
        row.setColumn('department name', name)
        pass
    return expectedResults


def getExpectedLeftJoinResults():
    expectedResults = RelationalModule.createTable(
        'join', ['surname', 'department id', 'department name'])
    for surname, id, name in [('Smith', 34, 'Clerical'),
                              ('Jones', 33, 'Engineering'),
                              ('Robinson', 34, 'Clerical'),
                              ('Steinberg', 33, 'Engineering'),
                              ('Rafferty', 31, 'Sales'),
                              ('Jasper', RelationalModule.Table.NULL, RelationalModule.Table.NULL)]:
        row = expectedResults.addRow()
        row.setColumn('surname', surname)
        row.setColumn('department id', id)
        row.setColumn('department name', name)
        pass
    return expectedResults


def getExpectedRightJoinResults():
    expectedResults = RelationalModule.createTable(
        'join', ['surname', 'department id', 'department name'])
    for surname, id, name in [('Smith', 34, 'Clerical'),
                              ('Jones', 33, 'Engineering'),
                              ('Robinson', 34, 'Clerical'),
                              ('Steinberg', 33, 'Engineering'),
                              ('Rafferty', 31, 'Sales'),
                              (RelationalModule.Table.NULL, 35, 'Marketing')]:
        row = expectedResults.addRow()
        row.setColumn('surname', surname)
        row.setColumn('department id', id)
        row.setColumn('department name', name)
        pass
    return expectedResults


def getExpectedFullJoinResults():
    expectedResults = RelationalModule.createTable(
        'join', ['surname', 'department id', 'department name'])
    for surname, id, name in [('Smith', 34, 'Clerical'),
                              ('Jones', 33, 'Engineering'),
                              ('Robinson', 34, 'Clerical'),
                              ('Jasper', RelationalModule.Table.NULL, RelationalModule.Table.NULL),
                              ('Steinberg', 33, 'Engineering'),
                              ('Rafferty', 31, 'Sales'),
                              (RelationalModule.Table.NULL, 35, 'Marketing')]:
        row = expectedResults.addRow()
        row.setColumn('surname', surname)
        row.setColumn('department id', id)
        row.setColumn('department name', name)
        pass
    return expectedResults


def getEmployeeTable():
    
    columns = ['surname', 'department id']
    table = RelationalModule.createTable(
        'employees', 
        columns
    )
    for surname, deptid in [('Rafferty', 31),
                            ('Jones', 33),
                            ('Steinberg', 33),
                            ('Robinson', 34),
                            ('Smith', 34),
                            ('Jasper', None)]:
        row = table.addRow()
        if surname:
            row.setColumn('surname', surname)
        if deptid:
            row.setColumn('department id', deptid)
    return table


def getDepartmentTable():
    
    columns = ['id', 'name']
    table = RelationalModule.createTable(
        'department', columns)
    for id, name in [(31, 'Sales'),
                     (33, 'Engineering'),
                     (34, 'Clerical'),
                     (35, 'Marketing')]:
        row = table.addRow()
        row.setColumn('id', id)
        row.setColumn('name', name)
    return table
    

def main():
    suite = unittest.makeSuite(TestCase,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

