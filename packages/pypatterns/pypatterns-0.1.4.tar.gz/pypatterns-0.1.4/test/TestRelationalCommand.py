import os
import sys
import unittest
import logging

APP_ROOT = os.getenv('APP_ROOT')
sys.path.insert(0, '%s/pypatterns/src' % APP_ROOT)
sys.path.insert(0, '%s/currypy/src' % APP_ROOT)


import pypatterns.command as CommandModule
import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule

sys.path.insert(0,"../data")

class TestCase(unittest.TestCase):

    COLUMNS = ['column1', 'column2', 'column3']
    
    
    def testTable(self):
        columns = TestCase.COLUMNS

        l = []

        command = CommandModule.CompositeCommand()

        command.addCommand(
            RelationalCommandModule.CreateTableCommand(
                'test',
                columns,
                l.append,
                l.remove
                )
            )

        command.do()
        table = l[0]

        command = CommandModule.CompositeCommand()
        rowValuesList = [
            [1,2,3],
            [1,'2','3'],
            [None,None,[]]
        ]
        for rowValues in rowValuesList:
            #row = table.addRow()
            #map(row.setColumn, columns, rowValues)
            l = []
            addRowCommand = RelationalCommandModule.AddRowCommand(
                table,
                l.append
                )
            command.addCommand(addRowCommand)
            for column, value in zip(columns, rowValues):
                commandBuilder = RelationalCommandModule.SetColumnValueCommandBuilder(
                    addRowCommand,
                    column,
                    value)
                command.addCommandBuilder(addRowCommand, commandBuilder)
                pass
            pass
                

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


    def testRemoveRows(self):
        table = self.buildDefaultTable()

        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1', FilterModule.IdentityFilter(1))
        
        command = RelationalCommandModule.RemoveRowsCommand(
            table, columnValueFilter)

        count = len(table.rows())
        assert count is not 0

        command.do()
        assert len(table.rows()) is 0

        command.undo()
        assert len(table.rows()) is count
        return

    
    def testModifyRow(self):
        table = self.buildDefaultTable()

        originalValue = 1
        column = 'column1'

        columnValueFilter = RelationalModule.ColumnValueFilter(
            column, FilterModule.IdentityFilter(originalValue))

        rows = [x for x in table.retrieveForModification(columnValueFilter)]

        command = RelationalCommandModule.SetColumnValueUsingRowFilterCommand(
            columnValueFilter, table, column, 2)
        command.do()
            
        columnValueFilter = RelationalModule.ColumnValueFilter(
            'column1', FilterModule.IdentityFilter(2))
        for rowValues in table.retrieve(columnValueFilter, [column]):
            assert rowValues[0] is 2
        
        command.undo()
        
        for row in rows:
            assert row.getColumn(column) is originalValue

        return


    def buildDefaultTable(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test', columns)

        row = table.addRow()
        rowValues = [1, '1', None]
        map(row.setColumn, columns, rowValues)
        
        return table

    
    # END class TestCase
    pass


    

def main():
    suite = unittest.makeSuite(TestCase,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

