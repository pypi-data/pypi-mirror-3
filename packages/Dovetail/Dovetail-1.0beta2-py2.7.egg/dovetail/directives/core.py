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

"""The core directives."""

# This class implements functions declared elsewhere and
# cannot control the arguments
# pylint: disable-msg=W0613
# The classes in this file are deliberately simple
# pylint: disable-msg=R0903

from functools import wraps
from dovetail.model import LoadedTask, Dependencies, TaskWrapper, Task
from dovetail.engine import PROCESSOR, STATE
from dovetail.util import Logger, NonZeroReturnCode, Skipped, FailIf

PREDICATE_ARG_CACHE = {}

def call_predicate(predicate, execution):
    """Calls a predicate, resolving whether the predicate uses the optional
    Execution argument, and returns the result of the call.

    This method caches whether the predicate uses the optional argument in
    the PREDICATE_ARG_CACHE.

    :param predicate: A function or callable which, when called,
                      returns True or False
    :type predicate:  function, callable
    :param execution: An Execution object containing current state
    :type execution:  Execution
    :return: The current value of the predicate
    :rtype: boolean
    """
    if type(predicate) == type:
        raise TypeError("Predicate {0} is a type, not an instance. Perhaps you need to call the constructor".format(predicate))
    try:
        with_arg = PREDICATE_ARG_CACHE[predicate]
    except KeyError:
        from inspect import getargspec
        try:
            spec = getargspec(predicate)
            # If any arguments or varargs, then we will call with an
            # execution object
            with_arg = spec[0] or spec[1]
        except TypeError:
            spec = getargspec(predicate.__call__)
            with_arg = len(spec[0]) > 1 or spec[1]
        PREDICATE_ARG_CACHE[predicate] = with_arg
    if with_arg:
        return predicate(execution)
    else:
        return predicate()

def coalesce(predicate, predicates):
    """Internal function to produce a single list from a mandatory predicate
    and an optional list of further predicates.

    :param predicate: A predicate
    :type predicate: function, callable
    :param predicates: A list or iterable of further Predicates, or None
    :type predicates: duck-typed iterable of Predicate
    :return: A list consisting of all Predicates
    :rtype list:
    """
    if predicates is None or len(predicates) == 0:
        return [ predicate ]
    else:
        result = list(predicates)
        result.insert(0, predicate)
        return result

def task(f):
    """The task directive declares that a function is a Dovetail Task and
    causes an Instance of LoadedTask (subclass of Task) to be instantiated
    and registered in the Dovetail model."""
    task_instance = LoadedTask(f)
    Logger.debug("Loaded " + str(task_instance))
    @wraps(f)
    def wrapped(*kw, **kwargs):
        """A decorator that prints a warning if a Task is called directly"""
        if PROCESSOR.current_task != task_instance:
            print "WARNING: {0}() has been called directly rather than by the Dovetail processor".format(f.__name__)
            print "         Dovetail directives and logging may not work as expected."
            print "         Use dovetail.build('{0}') instead".format(task_instance.name)
        return f(*kw, **kwargs)
    return wrapped

def depends(*tasks):
    """This is a declares that a task is dependent on another task completing before it can run.

    :param tasks: A comma separated list of task names or functions
    :type tasks: string, function"""
    assert not any(dependency for dependency in tasks
                         if not(isinstance(task, Task) or
                            hasattr(task, "__call__") or
                            isinstance(task, basestring))), \
            "@depends: Each argument must be a Task, the name of a Task or a function implementing a Task"

    def run_once(f):
        """A decorator that simply records the dependencies and returns
        the original function"""
        Dependencies.add(f, *tasks)
        # No decoration is actually done
        return f
    return run_once

def do_if(predicate, *predicates):
    """Executes this Task if all predicates are True.

    :param predicate: A predicate
    :type predicate: function or callable returning boolean
    :param predicates: Optional; additional predicates
    :type predicates: function or callable returning boolean"""
    predicates = coalesce(predicate, predicates)
    assert not(any(predicate for predicate in predicates
                    if not(hasattr(predicate, "__call__")))), \
            "@do_if: All predicate arguments must be callable"
    def before(execution):
        """Skips the Task if the predicates evaluate to False"""
        if execution.state in [ STATE.SKIPPED, STATE.FAILED ]:
            Logger.log("@do_if: Not evaluating because the task is {0}".format(execution.state))
            return
        for predicate in predicates:
            if call_predicate(predicate, execution):
                Logger.debug("@do_if: '{0}' evaluates to True".format(predicate))
            else:
                execution.skip("'{0}' is False".format(predicate))
    return TaskWrapper.decorator_maker("@do_if", before=before)

def skip_if(predicate, *predicates, **kwargs):
    """Skips this Task if all predicates are True; and optional message can be
    specified to make the logic clearer.

    The optional message is specified using \*\*kwargs: message='my message'.
    When given, this message will be logged to the Execution object (and
    the logging mechanism). This can be used to make complex logic more
    understandable in the output.

    :param predicate: A predicate
    :type predicate: function or callable returning boolean
    :param predicates: Optional; additional predicates
    :type predicates: function or callable returning boolean
    :param kwargs: kwargs. See above
    """
    predicates = coalesce(predicate, predicates)
    assert not(any(predicate for predicate in predicates
                    if not(hasattr(predicate, "__call__")))), \
              "@skip_if: All predicate arguments must be callable. Did you mean to set working='message'?"
    if not len(kwargs):
        string = [ str(predicate) for predicate in predicates ]
        message = "and ".join(string)
    elif len(kwargs) == 1:
        message = kwargs["message"]
    else:
        assert len(kwargs) <= 1, "kwargs may contain only a single argument, 'message'"

    def before(execution):
        """Loops over the predicates, executing them; before() returns
        immediately if any Predicate returns False."""
        if execution.state in [ STATE.SKIPPED, STATE.FAILED ]:
            Logger.log("@skip_if: Not evaluating because the task is {0}".format(execution.state))
            return
        for predicate in predicates:
            if call_predicate(predicate, execution):
                Logger.debug("@skip_if: '{0}' evaluates to True".format(predicate))
            else:
                Logger.major("@skip_if: '{0}' evaluates to False. Not skipping.".format(predicate))
                return
        execution.skip(message)

    return TaskWrapper.decorator_maker("@skip_if", before=before)

def fail_if(predicate, *predicates, **kwargs):
    """Fails the Task if all the predicates are True with optional failure
    message.

    The message may be assigned using \*\*kwargs: message='my message'
    If given, this message will be the message of the FailIf exception raised
    if the predicates return True. If not given, a default message will be
    constructed.

    fail_if runs after the main body of the Task has executed.

    :param predicate: A predicate
    :type predicate: function or callable returning boolean
    :param predicates: Optional; additional predicates
    :type predicates: function or callable returning boolean
    :param kwargs: kwargs. See above
    """
    predicates = coalesce(predicate, predicates)
    assert not(any(predicate for predicate in predicates
                    if not(hasattr(predicate, "__call__")))),\
            "@fail_if: All predicate arguments must be callable. Did you mean to set working='message'?"
    if not len(kwargs):
        message = None
    elif len(kwargs) == 1:
        message = kwargs["message"]
    else:
        assert len(kwargs) <= 1, "kwargs may contain only a single argument, 'message'"

    #noinspection PyUnusedLocal
    def after(execution, result):
        """Loops over the Predicates, evaluating them; if any predicate returns
        False, the Task is failed and the function immediately returns."""
        if execution.state in [ STATE.SKIPPED, STATE.ABORTED, STATE.FAILED, STATE.REPEATED ]:
            Logger.log("@fail_if: Not evaluating because the task is {0}".format(execution.state))
            return
        for predicate in predicates:
            if call_predicate(predicate, execution):
                if message is None:
                    msg = "FAILING {0} because {1}".format(execution.task.name, predicate)
                else:
                    msg = message
                Logger.error("@fail_if: {0}".format(msg))
                execution.fail(FailIf(msg))
                break
            else:
                Logger.debug("@fail_if: '{0}' evaluates to False.".format(predicate))

    return TaskWrapper.decorator_maker("@fail_if", after=after)


class Not(object):
    """A negation predicate which wraps another predicate.

    :class:`Not` instances are callable, optionally with an :class:`dovetail.engine.Execution`.
    Their return value is the boolean negation of the predicate which they wrap.

    Not's value is evaluated on demand, not when it is instantiated::

        n = Not(Env("BASH"))
        print p()    # Evaluation occurs here"""
    def __init__(self, predicate):
        self.predicate = predicate
        """:type: function or callable returning boolean"""

    def __call__(self, execution=None):
        return not call_predicate(self.predicate, execution)

    def __str__(self):
        return "Not({0})".format(self.predicate)

class Any(object):
    """A predicate that evaluates to True if any of its arguments is True.

    :class:`Any` instances are callable, optionally with an :class:`dovetail.engine.Execution`.
    This predicate has the same semantics as Pythons :func:`any` function.

    Instantiate with a comma separated list of predicates, or use Python's
    \*kw argument modifier::

        a = Any(p1, p2, p3)

    Or::

        l = [ p1, p2, p3 ]
        a = Any(*l)

    Any's value is evaluated on demand, not when it is instantiated::

        print a()
    """
    def __init__(self, *predicates):
        self.predicates = predicates
        """:type: iterable"""

    def __call__(self, execution=None):
        return any(call_predicate(predicate, execution) for predicate in self.predicates)

    def __str__(self):
        string = ", ".join(str(predicate) for predicate in self.predicates)
        return "Any({0})".format(string)

class All(object):
    """A predicate that returns True if all of its arguments are True.

    :class:`Any` instances are callable, optionally with an :class:`dovetail.engine.Execution`.
    This predicate has the same semantics as Pythons :func:`all` function.

    Instantiate with a comma separated list of predicates, or use Python's
    \*kw argument modifier::

        a = All(p1, p2, p3)

    Or::

        l = [ p1, p2, p3 ]
        a = All(*l)

    Any's value is evaluated on demand, not when it is instantiated::

        print a()
    """
    def __init__(self, *predicates):
        self.predicates = predicates
        """:type: iterable"""

    def __call__(self, execution=None):
        return all([ call_predicate(predicate, execution) for predicate in self.predicates ])

    def __str__(self):
        string = ", ".join(str(predicate) for predicate in self.predicates)
        return "All({0})".format(string)


def check_result(f):
    """Checks the return of the decorated function as if it were a shell script - anything
    other than None or 0 is considered an error and an exception will be thrown.

    This is similar to the longer::

        @fail_if(Not(ResultZero()))

    but issues a more specific message and exception"""
    def after(execution, result):
        """Implementation of the algorithm described in check_result()"""
        if execution.state in [ STATE.SKIPPED, STATE.ABORTED, STATE.FAILED, STATE.REPEATED ]:
            Logger.log("@check_result: skipping because the task is {0}".format(execution.state))
        if result is None or result == 0:
            Logger.debug("@check_result: Zero/None return")
        else:
            Logger.major("@check_result: FAILING: Non-zero return value: {0}".format(result))
            execution.fail(NonZeroReturnCode("Function {0} returned {1}".format(f.__name__, result)))
    return TaskWrapper.decorate("@check_result", f, after=after)

def fail_if_skipped(f):
    """If the wrapped Task was skipped by any directive, the Task will be failed.

    This is useful to force an error if the environment is, for example, not correct.

    This is similar to the longer::

        @fail_if(StateSkipped())

    but issues a more specific message and exception"""
    #noinspection PyUnusedLocal
    def after(execution, result):
        """Implementation of the algorithm described in fail_if_skipped"""
        if execution.state == STATE.SKIPPED:
            Logger.major("@fail_if_skipped: FAILING")
            reason = " and ".join(execution.skip_reasons)
            execution.fail(Skipped("{0} was skipped because {1}".format(execution.task, reason)))
        else:
            Logger.debug("@fail_if_skipped: Task was not skipped")
    return TaskWrapper.decorate("@fail_if_skipped", f, after=after)
