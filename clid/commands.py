#!/usr/bin/env python3

from . import const


class InvalidCommand(Exception):
    """Error raised when a command string is invalid"""
    pass


class InvalidCommandSyntax(Exception):
    """Error raised when there is a syntax error in the command string,
       like unwanted switches, args, misspelled switches, etc
    """
    pass


def command_without_switch_and_args(command_func):
    """Decorator for defining commands which do not accept switches or arguments"""
    def decorated(self, switch, args):
        if switch or args:
            raise InvalidCommandSyntax('This command does not accept switches or arguments')
        else:
            command_func(self)
    return decorated


class Commands(object):
    """Class which stores commands that are executed by the user, either through
       the command line or key-bindings.

       Attributes:
            app: Reference to the __main__.ClidApp
    """
    def __init__(self, parent):
        self.parent = parent

# TODO: do not execute command if command is not in form's scope
# TODO: aliases for commands
    def execute_command(self, command_str):
        """Execute `command_str`.

           Args:
                command_str(str): A string like "mark -i"
           Raises:
                InvalidCommand: If `command_str` is not a valid one
        """
        command, switch, args = const.COMMAND_REGEX.fullmatch(command_str).groups()
        try:
            getattr(self, command)(switch, args)
        except AttributeError:
            raise InvalidCommand('{command} does not exist'.format(command=command))

    @command_without_switch_and_args
    def quit(self):
        """Quit the app"""
        exit()
