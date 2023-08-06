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

"""Predicates about the processing of the engine."""

# The classes in this file are deliberately simple
# pylint: disable-msg=R0903

from dovetail.engine import STATE
from dovetail.util import Logger

class StateStarted(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.STARTED`"""
    def __call__(self, execution):
        return execution.state is STATE.STARTED

    def __str__(self):
        return "Task has Started"


class StateSkipped(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.SKIPPED`"""
    def __call__(self, execution):
        return execution.state is STATE.SKIPPED

    def __str__(self):
        return "Task was Skipped"


class StateFailed(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.FAILED`"""
    def __call__(self, execution):
        return execution.state is STATE.FAILED

    def __str__(self):
        return "Task Failed"


class StateAborted(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.FAILED`"""
    def __call__(self, execution):
        return execution.state is STATE.ABORTED

    def __str__(self):
        return "Task Aborted"


class StateRepeated(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.FAILED`"""
    def __call__(self, execution):
        return execution.state is STATE.REPEATED

    def __str__(self):
        return "Task was Repeated"


class StateSucceeded(object):
    """A predicate that returns True if the state of the current Task
    is :const:`.engine.STATE.SUCCEEDED`"""
    def __call__(self, execution):
        return execution.state is STATE.SUCCEEDED

    def __str__(self):
        return "Task Succeeded"


class StdErr(object):
    """A predicate that returns True if a task has produced output to
    :data:`sys.stderr`"""
    def __call__(self, execution):
        return execution.received_stderr()

    def __str__(self):
        return "Task wrote to sys.stderr"

class DependentSucceeded(object):
    """A predicate that returns True if the current task has at least one
    dependent Task that executed successfully.

    This is useful to detect a Task whose dependents all skipped"""
    def __call__(self, execution):
        for dependent in execution.dependents:
            if dependent.state is STATE.SUCCEEDED:
                Logger.log("{0} succeeded".format(dependent.task.name))
                return True
        Logger.major("No dependent of {0} succeeded".format(execution.task.name))
        return False

    def __str__(self):
        return "Dependent succeeded"


class ResultZero(object):
    """A predicate that returns True if a task returns 0 - i.e. what
    Unix considers a successful execution"""
    def __call__(self, execution):
        return execution.result == 0

    def __str__(self):
        return "Task returned 0"

class ResultNone(object):
    """A predicate that returns True if a task returns *None*"""
    def __call__(self, execution):
        return execution.result is None

    def __str__(self):
        return "Task returned None"

class ResultEquals(object):
    """A predicate that returns True if a task returns a specific value.

    :param result: The value to test for
    :type  result: *any*
    :return: True if the result equals **result**
    :rtype:  boolean"""
    def __init__(self, result):
        self.result = result

    def __call__(self, execution):
        return execution.result == self.result

    def __str__(self):
        return "Task returned {0}".format(self.result)

