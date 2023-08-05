import logging
import sys
import traceback

class Validator(object):

    def validate(self):
        raise NotImplementedError('have not implemented validate')

    # END class Validator
    pass


class NotValidator(Validator):

    def __init__(self, validator):
        self._validator = validator
        return

    def validate(self):
        return not self._validator.validate()

    # END class NotValidator
    pass

VALIDATOR_SUCCEED = Validator()
VALIDATOR_SUCCEED.validate = lambda: True

VALIDATOR_FAIL = NotValidator(VALIDATOR_SUCCEED)


class ValidationError(Exception):
    pass

class ExecutionError(Exception):
    pass

class Command(object):

    def __init__(self):
        self._hasExecuted = False
        self.validator(VALIDATOR_SUCCEED)
        return

    def validator(self, value=None):
        if value is not None:
            self._validator = value
        return self._validator

    def do(self):
        """
        This method is public API for executing commands
        and the one that's called by external objects,
        e.g. the command manager or the unittest
        The method in turn calls self.execute()
        """
        if self._hasExecuted:
            raise ValidationError('%s has already executed' % self)
        if not self._validator.validate():
            raise ValidationError('%s failed validation' % self)

        try:
            self.execute()
            self._hasExecuted = True
        except Exception, e:
            self.handleExecuteError()
            raise
        return

    def handleExecuteError(self):
        return

    def execute(self):
        """
        subclass just need to implement this
        and the complimentary unexecute method
        """
        raise NotImplementedError('have not implemented execute')

    def undo(self):
        """
        This method is public API for undoing commands
        and the one that's called by external objects,
        e.g. the command manager or the unittest
        The method in turn calls self.unexecute()
        """
        if not self._hasExecuted:
            raise ValidationError('%s has not yet executed' % self)

        self.unexecute()
        self._hasExecuted = False
        return

    def unexecute(self):
        """
        subclass just need to implement this
        and the complimentary execute method
        """
        raise NotImplementedError('have not implemented unexecute')

    # END class Command
    pass 


class CompositeCommand(Command):

    def __init__(self):
        Command.__init__(self)

        # we need both the list and the map
        # even though the keys to the map are the elements of the list
        # because the list maintains execution order
        # and the map maintains the command builders
        self._subcommands = []
        self._commandBuilders = {}

        self._executedCommands = []
        return


    def addCommand(self, command):
        self._subcommands.append(command)
        self._commandBuilders[command] = []
        return


    def addCommandBuilder(self, command, commandBuilder):
        """
        command builders are associated with a particular command
        they are called in the order in which they are appended
        """
        self._commandBuilders[command].append(commandBuilder)
        return

    def handleExecuteError(self):
        self.unexecute()
        return

    def execute(self):
        # TODO:
        # also need command builders that apply to the whole sequence
        # and not tied to any specific subcommand

        map(self._executeSubcommand, self._subcommands)

        pass


    def _executeSubcommand(self, command):
        generatedCommands = [command]
        for commandBuilder in self._commandBuilders[command]:
            commandBuilder.addCommandsPreExecute(generatedCommands)
            pass

        map(self._executeRawCommand, generatedCommands)

        # now run the command builders
        # and see if any commands need to be generated 
        # and executed post execution of the original command
        generatedCommands = []
        for commandBuilder in self._commandBuilders[command]:
            commandBuilder.addCommandsPostExecute(generatedCommands)
            pass

        map(self._executeRawCommand, generatedCommands)
        return


    def _executeRawCommand(self, command):
        try:
            command.do()
            self._executedCommands.append(command)
        except Exception, e:
            # undo the command
            # and raise
            # the thing executing self
            # is responsible for calling the undo
            logging.debug("failed _executeRawCommand >> %s" % e)
            # self.unexecute()
            raise
        return


    def unexecute(self):
        for subcommand in self._executedCommands.__reversed__():
            # need to call undo
            # and not unexecute
            # because we need undo to revert
            # the command's internal state values
            subcommand.undo()
            pass
        return

    # END class CompositeCommand
    pass



class CommandManager(object):

    def __init__(self):

        self._commandHistory = []
        self._endIndex = 0

        return

    def stackTrace(self, value=None):
        if value is not None:
            self._stackTrace = value
        if not hasattr(self, '_stackTrace'):
            self._stackTrace = None
        return self._stackTrace

    def do(self, command):
        try:
            command.do()

            # since the command was successful
            # we want to remove all the commands 
            # that have been undone 
            # but could still be redone
            numCommands = len(self._commandHistory)
            if not self._endIndex is numCommands:
                self._commandHistory = self._commandHistory[:self._endIndex-1]

            self._commandHistory.append(command)
            self._endIndex = len(self._commandHistory)
        except Exception, e:

            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            stackTrace = traceback.format_exception(
                exceptionType, exceptionValue, exceptionTraceback)
            self.stackTrace(stackTrace)

            return False

        return True

    def undo(self):
        if self._endIndex == 0:
            raise ValueError('cannot undo on an empty history')
        commandToUndo = self._commandHistory[self._endIndex-1]
        commandToUndo.undo()
        self._endIndex = self._endIndex - 1
        return
        

    # END class CommandManager
    pass


class CommandBuilder(object):
    """
    command builders allow for commands to be generated 
    during the execution of a composite command
    such that the generated commands become subcommands
    of that composite command
    """

    def __init__(self, command):
        self._command = command
        return

    def addCommandsPreExecute(self, commands):
        return

    def addCommandsPostExecute(self, commands):
        return

    # END class CommandBuilder
    pass
