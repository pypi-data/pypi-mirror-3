###############################################################################
# Dovetail:  A light-weight, multi-platform build tool for Python with
#            Continuous Integration servers like Jenkins in mind.
# Copyright (C) 2012, Aviser LLP, Singapore.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

"""Dovetail exceptions"""


def pp_exception(exception):
    """Pretty-print an exception"""
    return "{0}: {1}".format(type(exception).__name__, str(exception))

def stack_trace():
    """Obtains then prints a formatted stack-trace to std_err"""
    from sys import exc_info, stderr
    exc_type, exc_value, exc_traceback = exc_info()
    from traceback import print_exception
    print_exception(exc_type, exc_value, exc_traceback, file=stderr)


class DovetailException(Exception):
    """The superclass of all Dovetail exceptions"""
    pass


class CircularTaskDependency(DovetailException):
    """An exception raised when a Task has a circular reference on another Task.

    This is a condition that is detected at run-time.

    The Exception contains two members that record the dependency:

        * self.task: The Task on which the circular dependency was detected, and
        * self.stack: The call-stack at the point of the detection. The call-stack
          is a list of Tasks
    """
    def __init__(self, task, stack, *kw, **kwargs):
        DovetailException.__init__(self, *kw, **kwargs)
        self.task = task
        self.stack = list(stack)


class MissingRequirement(DovetailException):
    """An exception thrown when easy_install cannot resolve or install a requirement."""
    pass


class NoSuchModule(DovetailException):
    """An exception raised when either a module cannot be found (has not been
    loaded by Python, or when it is not a BuildModule"""
    pass


class NoSuchTask(DovetailException):
    """An exception raised when a Task is referenced and it has not be loaded"""
    pass


class NonZeroReturnCode(DovetailException):
    """An exception raised by @check_result when the task returns
    with a non-zero value"""
    pass


class Skipped(DovetailException):
    """An exception raised by the @fail_if_skipped directive if the Task was skipped:"""
    pass


class FailIf(DovetailException):
    """An exception raised by @fail_if when the predicate is False"""
    pass


class NoSuchDirectory(DovetailException):
    """An exception raised when a directive requires use of a directory which does
    not exist or is not readable"""
    pass


class CommandLineException(DovetailException):
    """The superclass of all exceptions that should be handled by the command-line
    routine and for which no stack trace should be printed"""
    def __init__(self, return_code, message):
        DovetailException.__init__(self, message)
        self.return_code = return_code

    def additional_help(self):
        """Returns an additional help string to help the user localize the problem"""
        from StringIO import StringIO
        from dovetail.config import print_usage
        string_buffer = StringIO()
        print_usage(string_buffer)
        message = string_buffer.getvalue()
        string_buffer.close()
        return message


class InvalidBuildFile(CommandLineException):
    """An exception raised when a build file is specified, but cannot be found,
    is not readable or has the wrong extension"""
    def __init__(self, message):
        CommandLineException.__init__(self, 33, message)


class InvalidEnvironment(CommandLineException):
    """An exception stating that the specified environment is badly configured, inaccessible
        or otherwise not valid"""
    def __init__(self, message):
        CommandLineException.__init__(self, 34, message)


class InvalidTask(CommandLineException):
    """An exception raised when a Task file is specified on the command line,
    but cannot be found"""
    def __init__(self, message):
        CommandLineException.__init__(self, 35, message)


class UnknownReport(CommandLineException):
    """An exception raised if requested to generate a report that is
    not known to it"""
    def __init__(self, return_code, message):
        CommandLineException.__init__(self, return_code, message)


class Terminate(CommandLineException):
    """An exception raised for a generic problem in parsing the command line
    arguments or if Dovetail crashes during a build.

    .. note::

        This is not raised if a build task fails or throws an exception"""
    def __init__(self, return_code, message):
        CommandLineException.__init__(self, return_code, message)

    def additional_help(self):
        return "Exception thrown in engine, directives or predicates"
