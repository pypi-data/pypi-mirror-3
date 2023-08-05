import pypatterns.command as CommandModule

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule


class CreateTableCommand(CommandModule.Command):

    def __init__(self, name, columns,
                 addToContextFunction, removeFromContextFunction):

        CommandModule.Command.__init__(self)

        self._addToContextFunction = addToContextFunction
        self._removeFromContextFunction = removeFromContextFunction

        self._tableName = name
        self._tableColumns = columns

        return


    def execute(self):

        table = RelationalModule.createTable(
            self._tableName, self._tableColumns)

        self._addToContextFunction(table)

        self._table = table
        return

    def unexecute(self):
        self._removeFromContextFunction(self._table)
        return

    pass


class AddRowCommand(CommandModule.Command):


    def __init__(self, table, addToContextFunction=None):
        CommandModule.Command.__init__(self)
        self._table = table
        self._addToContextFunction = addToContextFunction
        return

    def execute(self):
        row = self._table.addRow()
        self._row = row
        return

    def unexecute(self):
        filter = FilterModule.IdentityFilter(self._row)
        self._table.removeRows(filter)
        return
    
    # END class AddRowCommand
    pass


class SetColumnValueCommand(CommandModule.Command):

    def __init__(self, row, column, value):
        CommandModule.Command.__init__(self)
        self._row = row
        self._column = column
        self._newValue = value
        return

    def execute(self):
        self._originalValue = self._row.getColumn(self._column)
        self._row.setColumn(self._column, self._newValue)
        return

    def unexecute(self):
        self._row.setColumn(self._column, self._originalValue)
        return


    # END class SetColumnValueCommand
    pass

class SetColumnValueUsingRowFilterCommand(CommandModule.Command):

    def __init__(self, rowFilter, table, column, value):
        CommandModule.Command.__init__(self)
        self._rowFilter = rowFilter
        self._table = table
        self._column = column
        self._newValue = value
        return
    
    def execute(self):
        map = {}
        for row in self._table.retrieveForModification(self._rowFilter):
            map[row] = row.getColumn(self._column)
            row.setColumn(self._column, self._newValue)
            pass
        self._oldValueMap = map
        return

    def unexecute(self):
        for row, oldValue in self._oldValueMap.iteritems():
            row.setColumn(self._column, oldValue)
            pass

        return

    # END class SetColumnValueUsingRowFilterCommand
    pass


class SetColumnValueCommandBuilder(CommandModule.CommandBuilder):

    def __init__(self, command, column, value):
        CommandModule.CommandBuilder.__init__(self, command)
        self._column = column
        self._value = value
        return

    def addCommandsPostExecute(self, commands):
        
        commands.append(
            SetColumnValueCommand(
                self._command._row,
                self._column,
                self._value)
            )
        
        return

    # END class SetColumnValueCommandBuilder
    pass


class RemoveRowsCommand(CommandModule.Command):

    def __init__(self, table, filter):
        CommandModule.Command.__init__(self)
        self._table = table
        self._filter = filter
        return

    def execute(self):
        # save off the rows to be deleted
        removedRows = self._table.removeRows(self._filter)
        self._removedRows = removedRows
        return

    def unexecute(self):
        # restore the deleted rows
        map(self._table.addRow, self._removedRows)
        return

    # END class RemoveRowsCommand
    pass

