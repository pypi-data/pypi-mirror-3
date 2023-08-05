import logging
import sys
import os
import unittest

APP_ROOT = os.getenv('APP_ROOT')
sys.path.insert(0, '%s/pypatterns/src' % APP_ROOT)

import pypatterns.command as CommandModule

class HasKeyValidator(CommandModule.Validator):

    def __init__(self, map, key):
        self._map = map
        self._key = key
        return

    def validate(self):
        return self._key in self._map

    # END HasKeyValidator
    pass


class AddKeyCommand(CommandModule.Command):

    def __init__(self, map, key):
        CommandModule.Command.__init__(self)
        self._map = map
        self._key = key
        return

    def execute(self):
        self._map[self._key] = None
        return
    
    def unexecute(self):
        del self._map[self._key]
        return

    # END class AddKeyCommand
    pass


class FailCommand(CommandModule.Command):

    def execute(self):
        raise CommandModule.ExecutionError('this command always fails')

    # END class FailCommand
    pass

class SetValueCommand(CommandModule.Command):
    
    def __init__(self, map, key, value):
        CommandModule.Command.__init__(self)
        self._map = map
        self._key = key
        self._value = value
        return

    def execute(self):
        self._originalValue = self._map[self._key]
        self._map[self._key] = self._value
        return

    def unexecute(self):
        self._map[self._key] = self._originalValue
        delattr(self, '_originalValue')
        return
        

    # END SetValueCommand
    pass


class DeleteKeyCommand(CommandModule.Command):

    def __init__(self, map, key):
        CommandModule.Command.__init__(self)
        self._map = map
        self._key = key
        return

    def execute(self):
        self._originalValue = self._map[self._key]
        del self._map[self._key]
        return

    def unexecute(self):
        self._map[self._key] = self._originalValue
        return

    # END DeleteKeyCommand
    pass

class CommandBuilder1(CommandModule.CommandBuilder):
    
    
    def addCommandsPreExecute(self, commands):

        map = self._command._map
        key = self._command._key

        commands.insert(0, AddKeyCommand(map, key))

        return


    # END class CommandBuilder1
    pass


class CommandBuilder2(CommandModule.CommandBuilder):

    def __init__(self, command, value):
        CommandModule.CommandBuilder.__init__(self, command)
        self._value = value
        return

    def addCommandsPostExecute(self, commands):

        map = self._command._map
        key = self._command._key

        commands.append(SetValueCommand(map, key, self._value))
        
        return

    # END class CommandBuilder
    pass

class FailCommandBuilder1(CommandModule.CommandBuilder):
    def addCommandsPreExecute(self, commands):
        commands.insert(0, FailCommand())
        return

    # END class FailCommandBuilder1
    pass

class FailCommandBuilder2(CommandModule.CommandBuilder):
    def addCommandsPreExecute(self, commands):
        commands.append(FailCommand())
        return

    # END class FailCommandBuilder2
    pass

class FailCommandBuilder3(CommandModule.CommandBuilder):
    def addCommandsPostExecute(self, commands):
        commands.append(FailCommand())
        return

    # END class FailCommandBuilder3
    pass


class TestCommand(unittest.TestCase):


    def testValidator1(self):
        map = {}
        key = 1
        validator = HasKeyValidator(map, key)
        assert not validator.validate()

        notValidator = CommandModule.NotValidator(validator)
        assert notValidator.validate()
        return

    def testValidator2(self):
        key = 1
        map = {key:None}
        validator = HasKeyValidator(map, key)
        assert validator.validate()

        notValidator = CommandModule.NotValidator(validator)
        assert not notValidator.validate()
        return


    def testAddKeyCommand1(self):
        """
        verify that the basic command execute works
        """
        map = {}
        key = 1
        command = AddKeyCommand(map, key)
        validator = CommandModule.NotValidator(
            HasKeyValidator(map, key)
            )
        command.validator(validator)
        command.do()

        assert key in map

        command.undo()
        assert not key in map

        return

    def testAddKeyCommand2(self):
        """
        verify that the basic command execute works
        """
        key = 1
        map = {key:None}
        command = AddKeyCommand(map, key)
        validator = CommandModule.NotValidator(
            HasKeyValidator(map, key)
            )
        command.validator(validator)

        self.assertRaises(CommandModule.ValidationError, command.do)

        return

    def testSetValueCommand1(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}
        command = SetValueCommand(map, key, value)
        validator = HasKeyValidator(map, key)
        command.validator(validator)

        self.assertRaises(CommandModule.ValidationError, command.do)

        return

    def testSetValueCommand2(self):
        """
        """
        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}
        command = SetValueCommand(map, key, newValue)
        validator = HasKeyValidator(map, key)
        command.validator(validator)

        command.do()
        assert map[key] == newValue
        
        command.undo()
        assert map[key] == originalValue

        return

    def testCompoundCommand1(self):
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)

        addKeyCommand = AddKeyCommand(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)
        addKeyCommand.validator(notHasKeyValidator)

        command.addCommand(addKeyCommand)

        setValueCommand = SetValueCommand(map, key, value)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        command.do()
        assert map[key] == value

        command.undo()

        assert not key in map
        
        return

    def testCompoundCommand2(self):
        """
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(hasKeyValidator)
        command.addCommand(deleteKeyCommand)

        command.do()
        assert not key in map

        command.undo()
        assert map[key] == originalValue
        
        return

    def testCompoundCommand3(self):
        """
        test that if a subcommand fails because of a validator, 
        then everything is rolled back
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        failValidator = CommandModule.VALIDATOR_FAIL

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(failValidator)
        command.addCommand(deleteKeyCommand)

        try:
            command.do()
            assert False, 'expected command to fail'
        except CommandModule.ValidationError, e:
            assert map[key] == originalValue, 'map[%s] = %s' % (key, map[key])
            pass
        
        return

    def testCompoundCommand4(self):
        """
        verifies that if a subcommand fails during execution
        then all subcommands are rolled back
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(hasKeyValidator)
        command.addCommand(deleteKeyCommand)

        failCommand = FailCommand()
        command.addCommand(failCommand)


        try:
            command.do()
            assert False, 'expected command to fail'
        except CommandModule.ExecutionError, e:
            assert map[key] == originalValue, 'map[%s] = %s' % (key, map[key])
            pass

        return


    def testCommandBuilder1(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        setValueCommand = SetValueCommand(map, key, value)
        commandBuilder = CommandBuilder1(setValueCommand)

        command.addCommand(setValueCommand)
        command.addCommandBuilder(setValueCommand, commandBuilder)

        command.do()

        assert map[key] == value

        command.undo()

        assert not key in map

        return

    def testCommandBuilder2(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        addKeyCommand = AddKeyCommand(map, key)
        commandBuilder = CommandBuilder2(addKeyCommand, value)

        command.addCommand(addKeyCommand)
        command.addCommandBuilder(addKeyCommand, commandBuilder)

        command.do()

        assert map[key] == value

        command.undo()

        assert not key in map

        return


    def testFailCommandBuilder(self):
        """
        this will tests that the command is undone
        if a command added by the command builder fails
        regardless if its added before or after the execution
        """

        key = 1
        value = 'foo'
        map = {}


        for builderClass in [FailCommandBuilder1,
                             FailCommandBuilder2,
                             FailCommandBuilder3]:

            command = CommandModule.CompositeCommand()

            addKeyCommand = AddKeyCommand(map, key)
            commandBuilder = CommandBuilder2(addKeyCommand, value)

            command.addCommand(addKeyCommand)
            command.addCommandBuilder(addKeyCommand, commandBuilder)

            failCommandBuilder = builderClass(addKeyCommand)
            command.addCommandBuilder(addKeyCommand, failCommandBuilder)

            self.assertRaises(CommandModule.ExecutionError, command.do)

            assert len(map) is 0
            pass

        return


    # END class TestCommand
    pass



class TestCommandManager(unittest.TestCase):

    def setUp(self):
        self.commandManager = CommandModule.CommandManager()
        return
        
    def testAddKeyCommand1(self):
        """
        verify that the basic command execute works
        """
        map = {}
        key = 1
        command = AddKeyCommand(map, key)
        validator = CommandModule.NotValidator(
            HasKeyValidator(map, key)
            )
        command.validator(validator)

        self.commandManager.do(command)

        assert key in map

        self.commandManager.undo()

        assert not key in map

        return


    def testAddKeyCommand2(self):
        """
        verify that the basic command execute works
        """
        key = 1
        map = {key:None}
        command = AddKeyCommand(map, key)
        validator = CommandModule.NotValidator(
            HasKeyValidator(map, key)
            )
        command.validator(validator)

        self.assertTrue(key in map)
        self.commandManager.do(command)
        self.assertTrue(key in map)

        return

    def testSetValueCommand1(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}
        command = SetValueCommand(map, key, value)
        validator = HasKeyValidator(map, key)
        command.validator(validator)

        self.assertFalse(key in map)
        self.assertFalse(self.commandManager.do(command))
        self.assertTrue(self.commandManager.stackTrace() is not None)
        self.assertFalse(key in map)

        return

    def testSetValueCommand2(self):
        """
        """
        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}
        command = SetValueCommand(map, key, newValue)
        validator = HasKeyValidator(map, key)
        command.validator(validator)

        self.commandManager.do(command)
        assert map[key] == newValue
        
        self.commandManager.undo()
        assert map[key] == originalValue

        return

    def testCompoundCommand1(self):
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)

        addKeyCommand = AddKeyCommand(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)
        addKeyCommand.validator(notHasKeyValidator)

        command.addCommand(addKeyCommand)

        setValueCommand = SetValueCommand(map, key, value)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        self.commandManager.do(command)
        assert map[key] == value

        self.commandManager.undo()
        assert not key in map
        
        return

    def testCompoundCommand2(self):
        """
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(hasKeyValidator)
        command.addCommand(deleteKeyCommand)

        self.commandManager.do(command)
        assert not key in map

        self.commandManager.undo()
        assert map[key] == originalValue
        
        return

    def testCompoundCommand3(self):
        """
        test that if a subcommand fails because of a validator, 
        then everything is rolled back
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        failValidator = CommandModule.VALIDATOR_FAIL

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(failValidator)
        command.addCommand(deleteKeyCommand)

        self.assertEquals(map[key], originalValue)
        self.assertFalse(self.commandManager.do(command))
        self.assertTrue(self.commandManager.stackTrace() is not None)
        self.assertEquals(map[key], originalValue)

        return



    def testCompoundCommand4(self):
        """
        verifies that if a subcommand fails during execution
        then all subcommands are rolled back
        """

        key = 1
        originalValue = 'original'
        newValue = 'foo'
        map = {key:originalValue}

        command = CommandModule.CompositeCommand()

        hasKeyValidator = HasKeyValidator(map, key)
        notHasKeyValidator = CommandModule.NotValidator(hasKeyValidator)

        setValueCommand = SetValueCommand(map, key, newValue)
        setValueCommand.validator(hasKeyValidator)
        command.addCommand(setValueCommand)

        deleteKeyCommand = DeleteKeyCommand(map, key)
        deleteKeyCommand.validator(hasKeyValidator)
        command.addCommand(deleteKeyCommand)

        failCommand = FailCommand()
        command.addCommand(failCommand)

        self.assertEquals(map[key], originalValue)
        self.assertFalse(self.commandManager.do(command))
        self.assertTrue(self.commandManager.stackTrace() is not None)
        self.assertEquals(map[key], originalValue)

        return


    def testCommandBuilder1(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        setValueCommand = SetValueCommand(map, key, value)
        commandBuilder = CommandBuilder1(setValueCommand)

        command.addCommand(setValueCommand)
        command.addCommandBuilder(setValueCommand, commandBuilder)

        self.commandManager.do(command)
        assert map[key] == value

        self.commandManager.undo()
        assert not key in map

        return

    def testCommandBuilder2(self):
        """
        """
        key = 1
        value = 'foo'
        map = {}

        command = CommandModule.CompositeCommand()

        addKeyCommand = AddKeyCommand(map, key)
        commandBuilder = CommandBuilder2(addKeyCommand, value)

        command.addCommand(addKeyCommand)
        command.addCommandBuilder(addKeyCommand, commandBuilder)

        self.commandManager.do(command)
        assert map[key] == value

        self.commandManager.undo()
        assert not key in map

        return


    def testFailCommandBuilder(self):
        """
        this will tests that the command is undone
        if a command added by the command builder fails
        regardless if its added before or after the execution
        """

        key = 1
        value = 'foo'
        map = {}


        for builderClass in [FailCommandBuilder1,
                             FailCommandBuilder2,
                             FailCommandBuilder3]:

            command = CommandModule.CompositeCommand()

            addKeyCommand = AddKeyCommand(map, key)
            commandBuilder = CommandBuilder2(addKeyCommand, value)

            command.addCommand(addKeyCommand)
            command.addCommandBuilder(addKeyCommand, commandBuilder)

            failCommandBuilder = builderClass(addKeyCommand)
            command.addCommandBuilder(addKeyCommand, failCommandBuilder)

            self.assertTrue(len(map) is 0)
            self.assertFalse(self.commandManager.do(command))
            self.assertTrue(self.commandManager.stackTrace() is not None)
            self.assertTrue(len(map) is 0)

            pass

        return



    pass



def configLogging():
    """
    this will be called by all the main functions 
    to use the default setup for logging
    """
    # define a basic logger to write to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/tmp/pypatterns.log',
                        filemode='w')

    # define a handler to write to stderr
    # console = logging.StreamHandler()
    # set the level of this to verbosity of severity 'warning'
    # console.setLevel(logging.WARNING)
    # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    # console.setFormatter(formatter)
    # add the handler to the root logger
    # logging.getLogger('').addHandler(console)

    # end def configureLogging
    pass





def main():

    configLogging()

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase, 'test'))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

