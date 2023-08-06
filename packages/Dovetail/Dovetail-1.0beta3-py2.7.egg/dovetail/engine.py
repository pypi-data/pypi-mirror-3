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

"""The processing engine and state objects."""

from dovetail.model import Task, NULL_TASK
from dovetail.util import get_virtual_environment
from dovetail.loader import BuildModule
from dovetail.util import CircularTaskDependency, NoSuchDirectory, Logger, \
    pp_exception, tree, NoSuchTask
from dovetail.util.utilities import enum
from dovetail.util.logging import Message, StdErr

from datetime import datetime
from os import chdir, getcwd, environ, access, path, R_OK
from sys import exc_info

STATE = enum(STARTED=0, DEPENDENTS=1, RUNNING=2, CALLING=3,
             SUCCEEDED=4, FAILED=5, SKIPPED=6, ABORTED=7,
             REPEATED=8)
"""An enumeration capturing the state of execution.

:class:`Execution` is modelled as a state machine with the following states:

    0. STATE.STARTED: The :class:`Execution` instance has been freshly created
    1. STATE.DEPENDENTS: The :class:`Processor` is executing the :class:`.Task`
       dependencies from :class:`.Dependencies`
    2. STATE.RUNNING: The :class:`Processor` is executing the main body of the
       :class:`.Task`
    3. STATE.CALLING: A :class:`.Task` is programmatically calling another
       :class:`.Task`
    4. STATE.SKIPPED: Directives caused the :class:`.Task` to be skipped
       (not executed) but treated as successful
    5. STATE.SUCCEEDED: The :class:`.Task` completed normally
    6. STATE.FAILED: The :class:`.Task` itself failed (raising an exception)
    7. STATE.ABORTED: A dependent :class:`.Task` of this :class:`.Task` failed.
       The :class:`Processor` makes no attempt to run the main body of the
       :class:`.Task`
    8. STATE.REPEATED: A :class:`.Task` had already been executed (perhaps
       as a dependency or directly invoked); it is not executed again

And models state transitions as:

.. parsed-literal::
          .---------------------------------------------------.
         /  .-----------------------------------> SKIPPED >--.|
        /  /  .----------------------.                       ||
       /  /  /                       |   .------> SUCCEEDED  ||
      /  /  /                        v  /                    ||
     STARTED ---> DEPENDENTS ---> RUNNING >-----> FAILED <---+'
        |             |            |   ^            ^
        v             v            v   |            |
     REPEATED      ABORTED        CALLING >---------'

.. note::

     * If a directive fails in :meth:`.TaskWrapper.before` or
       :meth:`.TaskWrapper.after` the state will transition directly to
       FAILED and the system will stop
     * If @fail_if_skipped is used, then SKIPPED will transition to FAILED
     * The DEPENDENTS state will be skipped if there are no dependents
     * If a dependent :class:`Task` fails, the parent is then ABORTED
     * RUNNING transits to CALLING if the :class:`Task` calls
       :func:`build`. Normally this returns to RUNNING, but if the called
       Task fails, the calling task transitions to FAILED
"""

class Result(object):
    """The results of executing a build.

    Result is constructed by :class:`Processor` after the build has
    completed, successfully or otherwise.

    :param execution: The top-level stack frame
    :type  execution: :class:`Execution`

    Attributes:

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | task         | :class:`.Task`       | A reference to the Task that ran. If the |
    |              |                      | build was launched with multiple tasks   |
    |              |                      | this will be the :class:`.NullTask`      |
    +--------------+----------------------+------------------------------------------+
    | success      | boolean              | A boolean indicating if this run was     |
    |              |                      | successful or not                        |
    +--------------+----------------------+------------------------------------------+
    | result       | *any*                | The return value of the Task (if         |
    |              |                      | successful)                              |
    +--------------+----------------------+------------------------------------------+
    | execution    | :class:`Execution`   | A reference to the Execution instance    |
    |              |                      | containing a complete history of the run |
    +--------------+----------------------+------------------------------------------+
    | exception    | :class:`Exception`   | If the run failed, the Exception that    |
    |              |                      | was thrown from the failing Task         |
    +--------------+----------------------+------------------------------------------+
    | exc_type,    |                      | Details from the exception retrieved by  |
    | exc_value,   |                      | :func:`sys.exc_info`.                    |
    | exc_traceback|                      |                                          |
    +--------------+----------------------+------------------------------------------+
    """
    BANNER = """
===============================================================================
{0}

  Task '{1}' {2}

  Environment:
    Hostname:    {3}
    Username:    {4}
    Python:      {5}
    Working dir: {6}
    Build file:  {7}
    Tasks:       {8}
    Elapsed:     {9:.3f}s

===============================================================================
{10}
"""
    def __init__(self, execution):
        assert execution is not None
        assert isinstance(execution, Execution)
        assert execution.is_complete()
        self.task          = execution.task
        self.execution     = execution
        self.result        = execution.result
        self.exception     = execution.exception
        self.success       = execution.state in [ STATE.SUCCEEDED, STATE.REPEATED, STATE.SKIPPED] and \
                             self.exception is None

        if not self.success:
            assert self.exception is not None, \
                    "The Result is not successful, but no exception has been set"
            assert isinstance(self.exception, BaseException), \
                    "The Result is not successful and the object set as an Exception \
                     is not an instance of a subclass of BaseException"

    def report_tree(self):
        """Produce a report of the structure of the Tasks and their results"""
        def execution_timing(execution):
            """Returns the string representation for an execution instance
            in this report"""
            return "{0}\nElapsed: {1:.3f}s, internal: {2:.3f}".\
            format(str(execution), execution.duration(), execution.duration_internal())

        print 'Task structure and results'
        tree(self.execution,
             lambda e: e.dependents,
             display_root=self.execution.task is not NULL_TASK,
             node_text=execution_timing )

    def report_slowest(self):
        """Report the slowest tasks in the build (comprising >80% of build
        time, and being faster than 1ms)"""
        #TODO: From the total time, compute how the precision of the report to 3 sig fig.
        # eg, if longest task is 1000s, don't show milliseconds
        # Compute the smallest time considered in the report
        slowest = self.execution.executions_by_duration()
        print "Slowest Tasks:"
        total = self.execution.duration()
        upto = total * 0.8  # 80% of build time
        count = 0.0
        for execution in slowest:
            time = execution.duration_internal()
            if time < 0.001:
                # Simply not worth reporting anything less than 1ms
                break
            count += time
            print "{0:9.3f}s: {1}".format(time, execution.task)
            if count >= upto:
                break

        if count == 0.0:
            print "No task took more than 1ms"
        else:
            print "=========="
            print "{0:9.3f}s  (Total build time: {1:.3f}s)".format(count, total)
            print "All other tasks sum to less than 20% total build time, or took less than 1ms"

    def top_level_tasks(self):
        """Returns a list of the the top-level Tasks that were executed.

        If the top-level task is the logical grouping task, this will return the
        logical grouping's dependents"""
        if self.execution.task is NULL_TASK:
            return [ execution.task for execution in self.execution.dependents ]
        else:
            return [ self.execution.task ]

    def format_exception(self):
        """Returns a formatted exception message, exactly as Python
        does, for the exc_type, exc_value and exc_traceback attributes.

        Convenience method - delegates to the topmost execution object.

        If no exception this method returns the empty string"""
        failed = self.execution.find_failed()
        if failed is None:
            return ""
        else:
            return failed.format_exception()

    def banner(self):
        """Returns a report banner including most information required to
        identify this build"""
        from platform import node
        from getpass import getuser
        from sys import executable
        tasks = [ task.name for task in self.top_level_tasks() ]

        python = executable
        if get_virtual_environment():
            python += " (virtualenv slave)"

        now = datetime.now().replace(microsecond=0)

        return Result.BANNER.format(now.isoformat(sep=' '),
                                    ", ".join(tasks),
                                    self.__str__(),
                                    node(),
                                    getuser(),
                                    python,
                                    path.dirname(BuildModule.root.file_name),
                                    path.basename(BuildModule.root.file_name),
                                    self.execution.count(),
                                    self.execution.duration(),
                                    self.format_exception())

    def __str__(self):
        if self.success:
            return "SUCCESS, returning {0}".format(self.result)
        else:
            failed = self.execution.find_failed()
            if failed:
                task = failed.task
                return "FAILED\n    In file:  {0}\n    Task:     {1}\n    Message:  {2}".\
                        format(task.module.__file__,
                               task.func_name,
                               pp_exception(self.exception))
            else:
                return "FAILED\n    No task ran"


class Execution(object):
    """A stack frame recording the internal and external aspects of
    processing a Task and its dependents.

    :param task: The task whose execution is recorded
    :type  task: :class:`.Task`

    The :class:`Execution` stack is returned to by :func:`build` function wrapped in
    a :class:`Result`.

    Attributes:

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | task         | :class:`.Task`       | A reference to the Task that ran.        |
    +--------------+----------------------+------------------------------------------+
    | state        | Enum from            | Record of the state of the processing.   |
    |              | :data:`STATE`        | See state table see :data:`STATE`        |
    +--------------+----------------------+------------------------------------------+
    | start,       | :class:`datetime.\   | Start and end time of processing. If the |
    | finish       | datetime`            | processing has not finished, **finish**  |
    |              |                      | is *None*                                |
    +--------------+----------------------+------------------------------------------+
    | parent       | :class:`Execution`   | The :class:`Execution` instance that     |
    |              |                      | directly or indirectly invoked this task |
    +--------------+----------------------+------------------------------------------+
    | dependents   | list of              | List of :class:`Execution` instances of  |
    |              | :class:`Execution`   | direct or indirect task invocations      |
    +--------------+----------------------+------------------------------------------+
    | skip_reasons | list of string       | Accumulated messages from @skip_if,      |
    |              |                      | @do_if or any other cause                |
    |              |                      | of this task being skipped               |
    +--------------+----------------------+------------------------------------------+
    | result       | *any*                | The return value of the Task (if         |
    |              |                      | successful)                              |
    +--------------+----------------------+------------------------------------------+
    | exception    | :class:`Exception`   | If the task failed, the Exception that   |
    |              |                      | was thrown from the Task                 |
    +--------------+----------------------+------------------------------------------+
    | exc_type,    |                      | Details from the exception retrieved by  |
    | exc_value,   |                      | :func:`sys.exc_info`.                    |
    | exc_traceback|                      |                                          |
    +--------------+----------------------+------------------------------------------+
    """
    def __init__(self, task):
        assert task is not None
        assert isinstance(task, Task)
        self.start         = datetime.now()
        self.state         = STATE.STARTED
        self.parent        = None
        self.dependents    = []
        self._last_dep     = None
        self.task          = task
        self.finish        = None
        self.skip_reasons  = []
        self.result        = None
        self.exception     = None
        self.exc_type      = None
        self.exc_value     = None
        self.exc_traceback = None
        self._log          = []
        self._store        = {}

    def log(self, message):
        """Log a message to be recorded on the Execution object.

        :param message: A message
        :type  message: string

        This may later be retrieved programmatically or reported"""
        self._log.append(message)

    def depth(self):
        """Returns the depth of this call in the call stack.

        :return: Depth of this :class:`Execution` in the call stack
        :rtype:  int
        """
        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.depth()

    def get_messages(self):
        """Returns a list of Message objects that were logged.

        :return: Messages recorded during the execution of the task
        :rtype:  list of :class:`.Message`
        """
        return [ message for message in self._log if isinstance(message, Message) ]

    def received_stderr(self):
        """Returns true if the Execution received any error messages from stderr.

        :return: Did this task generate output on stderr?
        :rtype: boolean
        """
        return any(item for item in self._log if isinstance(item, StdErr))

    def _log_transition(self, to_state):
        """Helper function that logs the transition from one state to another."""
        Logger.debug("State transition: {0} {1} -> {2}".format(
            self.task,
            STATE.as_str(self.state),
            STATE.as_str(to_state)))

    def add_dependent(self, execution):
        """Adds another Execution instance as a child of this.

        :param execution: A child task of this
        :type  execution: :class:`Execution`
        """
        assert execution is not None
        assert isinstance(execution, Execution)
        assert self.state is STATE.STARTED or\
               self.state is STATE.DEPENDENTS or\
               self.state is STATE.RUNNING or\
               self.state is STATE.CALLING

        if self.state is STATE.STARTED:
            self._log_transition(STATE.DEPENDENTS)
            self.state = STATE.DEPENDENTS

        self.dependents.append(execution)
        self._last_dep = execution
        self._log.append(execution)
        execution.parent = self

    def internal(self):
        """Set the state of the :class:`Execution` to indicate processing of
        the internal task itself (dependencies complete)"""
        self._log_transition(STATE.RUNNING)
        assert self.state is STATE.STARTED or\
               self.state is STATE.DEPENDENTS
        self.state = STATE.RUNNING

    def call_started(self):
        """Set the state of the `Execution` to indicate that a :class:`.Task` has called
        :func:`build` to run another :class:`.Task`.

        This state continues only until the called :class:`Task` returns"""
        self._log_transition(STATE.CALLING)
        assert self.state is STATE.RUNNING
        self.state = STATE.CALLING

    def call_ended(self):
        """Set the state of the class:`Execution` to indicate that a
        :class:`.Task` has called :func:`build` and that task has completed"""
        self._log_transition(STATE.RUNNING)
        assert self.state is STATE.CALLING
        self.state = STATE.RUNNING

    def set_result(self, result):
        """Sets the result of the :class:`.Task`.

        .. Note ::

            This has to be set before the :class:`.Task` is said to be complete
            because the :meth:`.TaskWrapper.after` directives may fail the overall result
        """
        assert self.state is STATE.RUNNING
        self.result = result

    def succeed(self):
        """Set the state to indicate the execution was successful, capturing
        the result"""
        self._log_transition(STATE.SUCCEEDED)
        assert self.state is STATE.RUNNING
        self.state  = STATE.SUCCEEDED
        self.finish = datetime.now()

    def skip(self, reason):
        """Set the state to indicate the :class:`.Task` was skipped.

        :param reason: The reason for skipping the :class:`.Task`
        :type  reason: string
        """
        self._log_transition(STATE.SKIPPED)
        if self.state is not STATE.SKIPPED:
            assert self.state is STATE.STARTED
            self.state  = STATE.SKIPPED
            self.finish = datetime.now()
        self.skip_reasons.append(reason)

    def fail(self, exception):
        """Set the state to indicate the :class:`.Task` failed with an exception.

        :param exception: The exception thrown by the task
        :type  exception: :class:`Exception`
        """
        self._log_transition(STATE.FAILED)
        if self.state is STATE.FAILED:
            Logger.major("The Task has already been failed. Ignoring")
            return
        if self.state is STATE.ABORTED:
            Logger.major("The Task has already been aborted. Ignoring")
            return
        assert self.state is STATE.STARTED or \
               self.state is STATE.RUNNING or \
               self.state is STATE.SKIPPED or \
               self.state is STATE.CALLING
        self.state     = STATE.FAILED
        self.exception = exception
        self.finish    = datetime.now()

    def abort(self):
        """Set the state to indicate that a dependency of the :class:`.Task`
        failed; this :class:`.Task` will be aborted"""
        self._log_transition(STATE.ABORTED)
        assert self.state is STATE.DEPENDENTS
        self.state     = STATE.ABORTED
        # Propagate exception from last child
        self.exception = self.dependents[-1].exception
        self.finish    = datetime.now()

    def repeated(self):
        """Set the state to indicate that this :class:`.Task` has already run"""
        self._log_transition(STATE.REPEATED)
        assert self.state is STATE.STARTED
        self.state     = STATE.REPEATED
        self.finish    = datetime.now()

    def system_exception(self, exception):
        """Update the state to record that a system exception has occurred, and
        to fail the ongoing build.

        :param exception: A system exception thrown by Dovetail, a directive or predicate
        :type  exception: :class:`Exception`
        """
        self._log_transition(STATE.FAILED)
        self.state     = STATE.FAILED
        self.exception = exception
        self.finish    = datetime.now()

    def imprint_stack_trace(self):
        """Runs :func:`sys.exc_info` to stamp this object with the stack trace
        of the current exception"""
        self.exc_type, self.exc_value, self.exc_traceback = exc_info()

    def format_exception(self):
        """Returns a formatted exception message, exactly as Python
        does, for the exc_type, exc_value and exc_traceback attributes.

        :return: Formatted exception
        :rtype:  string"""
        if not self.has_stack_trace():
            return ""

        from traceback import format_exception
        tb = format_exception(self.exc_type, self.exc_value, self.exc_traceback)
        lines = ""
        for line in tb:
            lines += line
        return lines

    def has_stack_trace(self):
        """Returns *True* if this node failed and captured a stack trace"""
        return self.exc_type is not None

    def find_failed(self):
        """Searches the :class:`Execution` graph for the :class:`Execution`
        object which failed the build, either returning the Execution object or None

        :return: The :class:`Exception` which maps to the :class:`.Task`
                 which failed the build. Returns *None* if no exception
        :rtype:  :class:`Execution` or *None*
        """
        if self.state is STATE.FAILED:
            assert self.exception is not None
            return self
        elif self.state is STATE.ABORTED:
            # find the dependent which raised the exception
            assert self.exception is not None
            child = [ d for d in self.dependents if d.exception is self.exception ]
            assert child
            return child[0].find_failed()
        else:
            return None

    def duration(self):
        """Returns how long the task took, including dependencies.

        :return: Duration of execution
        :rtype:  float
        """
        return (self.finish - self.start).total_seconds()

    def duration_dependents(self):
        """Returns the duration that the dependencies of this Execution took
        to execute

        :return: Duration of dependency execution
        :rtype:  float
        """
        total = 0.0
        for dependent in self.dependents:
            total += dependent.duration()
        return total

    def duration_internal(self):
        """Returns the time inherent in processing the :class:`.Task`, i.e. less its
        dependencies

        :return: Duration of execution of the :class:`.Task`
        :rtype:  float
        """
        return self.duration() - self.duration_dependents()

    def executions_by_duration(self):
        """Returns a list of all executions from this point down the graph
        ordered by their elapsed internal duration (eg exclude) with the
        longest elapsed executions first"""
        executions = sorted(self.flatten(),
                            key=lambda execution: execution.duration_internal())
        executions.reverse()
        return executions

    def is_complete(self):
        """Is the :class:`.Task` complete?

        :return: Returns True if the Task has completed execution, successfully or not
        :type:   boolean
        """
        return self.state is STATE.SKIPPED   or\
               self.state is STATE.SUCCEEDED or\
               self.state is STATE.FAILED    or\
               self.state is STATE.ABORTED   or\
               self.state is STATE.REPEATED

    def is_ok(self):
        """Returns True if the Task has completed execution without error.

        :return: Returns True if :attr:`Execution.state` is
                 SKIPPED, SUCCEEDED or REPEATED
        :type:   boolean
        """
        return self.state is STATE.SKIPPED   or\
               self.state is STATE.SUCCEEDED or\
               self.state is STATE.REPEATED

    def flatten(self):
        """Returns a list containing this and all dependent Executions"""
        result = []
        def iterate(execution, result):
            """Recursively walk the tree of executions appending all execution
            instances to the list passed as the result argument"""
            result.append(execution)
            for child in execution.dependents:
                iterate(child, result)
        iterate(self, result)
        return result

    def count(self):
        """Returns the number of Execution instances in the tree.

        If this has no children, it will return 1"""
        c = 1
        for dependent in self.dependents:
            c += dependent.count()
        return c

    def store(self, key, value):
        """Stores the key-value pair in a dictionary in the Execution
        frame for later retrieval allowing multiple participants
        to share data.

        store() works in conjunction with retrieve() to create a:

            * Shared whiteboard - use simple keys such as strings, or
            * Private rendezvous for mementos - use a private key
              such as a function reference"""
        assert key is not None
        Logger.debug("Execution storing {0}={1}".format(key, value))
        self._store[key] = value

    def retrieve(self, key):
        """Retrieves a value from the Execution frame store

        Works in conjunction with store()."""
        value = self._store[key]
        Logger.debug("Execution retrieving: {0}={1}".format(key, value))
        return value

    def __str__(self):
        if self.state is STATE.STARTED:
            msg = "STARTING {0}".format(self.task)
        elif self.state is STATE.DEPENDENTS:
            msg = "Dependencies of {0}".format(self.task)
        elif self.state is STATE.RUNNING:
            msg = "Running {0}".format(self.task)
        elif self.state is STATE.CALLING:
            msg = "CALLING {0} is calling {1}".format(self.task, self.dependents[-1].task)
        elif self.state is STATE.SUCCEEDED:
            if self.result is None:
                result = ""
            else:
                result = " returned {0}".format(self.result)
            msg = "SUCCEEDED: {0}{1}".format(self.task, result)
        elif self.state is STATE.FAILED:
            msg = "FAILED: {0} raised {1}".format(self.task, pp_exception(self.exception))
        elif self.state is STATE.SKIPPED:
            msg = "SKIPPED: {0} because {1}".format(self.task, " and ".join(self.skip_reasons))
        elif self.state is STATE.ABORTED:
            msg = "ABORTED: {0} raised {1}".format(self.task, pp_exception(self.exception))
        elif self.state is STATE.REPEATED:
            msg = "REPEATED: {0}".format(self.task)
        else:
            raise Exception("Unknown state {0}".format(STATE.as_str(self.state)))
        return msg

class Processor(object):
    """The processor that runs tasks and their decorators and maintains a
    call stack of Execution instances.

    To run (or build) a :class:`Task`, use the :func:`build` function."""
    def __init__(self):
        self.call_stack    = []
        self.executions    = {}
        self.current_frame = None
        self.current_task  = None
        self.last_run      = None

    def _push_frame(self, task):
        """Adds a new execution frame onto the execution graph, updates
         current_frame and current_task, and returns the execution instance"""
        assert task is not None
        assert isinstance(task, Task)
        execution = Execution(task)
        if self.current_frame is not None:
            if self.current_frame.state is STATE.RUNNING:
                # this is an API call by the Task to call another rather than a dependency
                self.current_frame.call_started()
            self.current_frame.add_dependent(execution)

        self.call_stack.append(task)
        self.executions[task] = execution
        self.current_frame    = execution
        self.current_task     = task
        Logger.set_frame(execution)
        return execution

    def _pop_frame(self, task):
        """Updates the current_frame and current_task members to point to the parent of the
        current execution frame.

        :param task: The next task to execute
        :type  task: :class:`.Task`
        """
        current = self.call_stack.pop()
        assert task == current
        self.current_frame = self.current_frame.parent
        Logger.set_frame(self.current_frame)
        if self.current_frame is None:
            self.current_task = None
        else:
            if self.current_frame.state is STATE.CALLING:
                # The API call has returned.
                self.current_frame.call_ended()
            self.current_task  = self.current_frame.task

    def _get_execution_frame(self, task):
        """Searches for the execution frame for the Task passed as the argument.

        :param task: The Task to search for
        :type  task: :class:`.Task`
        :return: Execution stack frame for this task
        :rtype:  :class:`Execution`
        :raises:  :exc:`KeyError`
        """
        assert task is not None
        assert isinstance(task, Task)
        return self.executions.get(task)

    def _pp_call_stack(self):
        """Pretty-prints the call stack.

        :return: The call stack, suitable for displaying on the console
        :rtype:  string"""
        return " => ".join(task.name for task in self.call_stack)

    def _has_completed(self, task):
        """Returns True if the task has been executed (successfully or with errors)

        :param task: The Task being inquired
        :type  task: :class:`.Task`
        :return: Has the Task completed?
        :rtype:  boolean
        :raises:  :exc:`KeyError`
        """
        execution = self._get_execution_frame(task)
        return execution is not None and execution.is_complete()

    ################################################################################
    # Main processing loop
    def _execute(self, task):
        """Executes the nominated Dovetail Task, returning the resulting Execution frame."""
        # This is the core method of this implementation and it is
        # necessarily complex
        # pylint: disable-msg=R0912
        # pylint: disable-msg=R0914
        # pylint: disable-msg=R0915

        assert task is not None
        assert isinstance(task, Task)
        Logger.debug("Entering execute({0})".format(task.name))

        # Perform some checks _before_ the frame is added, since after we add it,
        # they will necessarily both be true
        circular = any(running for running in self.call_stack if task is running)
        completed = self._has_completed(task)

        # Add the execution frame and process
        wrappers     = task.get_wrappers()
        previous_dir = getcwd()
        target_dir   = task.get_working_directory()
        manage_working_directory = target_dir is not None
        execution    = self._push_frame(task)
        Logger.major(str(execution))
        try: # This try to ensure the call_stack is cleanly popped
            if completed:
                execution.repeated()
                return execution

            if circular:
                Logger.error("Detected a circular dependency on {0} in the call stack:".format(task))
                Logger.error("    " + self._pp_call_stack())
                raise CircularTaskDependency(task, self.call_stack, "{0} in: {1}".format(task, self._pp_call_stack()))

            # First check of working directory, before the TaskWrappers
            if manage_working_directory and previous_dir != target_dir:
                if path.isdir(target_dir) and access(target_dir, R_OK):
                    Logger.log("Changing working directory to {0}".format(target_dir))
                    chdir(target_dir)
                else:
                    execution.fail(NoSuchDirectory("Cannot change directory to {0} - it does not exist or is not readable".format(target_dir)))
                    return execution

            # Run the before() function of the TaskWrappers
            for wrapper in wrappers:
                wrapper.before(execution)

            result = None
            if execution.state not in [ STATE.SKIPPED, STATE.FAILED ] :
                # Iterate over dependencies executing them (depth first) if they have not been executed
                try:
                    dependencies = task.dependencies()
                except NoSuchTask as exception:
                    Logger.error("Failed to find dependency: {0}".format(str(exception)))
                    execution.fail(exception)
                    return execution

                if dependencies:
                    Logger.log("Running dependencies: {0}".
                            format(", ".join(d.name for d in dependencies)))
                else:
                    Logger.debug("No dependencies")

                for dependent in dependencies:
                    assert dependent is not None
                    Logger.debug("{0} needs {1}".format(task, dependent))
                    execute_dep = self._execute(dependent)
                    if not execute_dep.is_ok():
                        Logger.log("Dependency failed: {0}".format(execute_dep))
                        execution.abort()
                        break

                # Second check of working directory: ensure that anything the
                # dependents did is reverted here before the main body of the
                # Task runs
                if manage_working_directory and previous_dir != target_dir:
                    if path.isdir(target_dir) and access(target_dir, R_OK):
                        Logger.log("Changing working directory to {0}".format(target_dir))
                        chdir(target_dir)
                    else:
                        execution.fail(NoSuchDirectory("Cannot change directory to {0} - it does not exist or is not readable".format(target_dir)))
                        return execution

                # Main body of the Task
                if execution.state is not STATE.ABORTED:
                    try:
                        execution.internal()
                        Logger.major('v'*30)
                        result = task.get_function()()
                        Logger.major('^'*30)
                        execution.set_result(result)
                    except Exception as exception: # pylint: disable-msg=W0703
                        # Catching generic Exception because we really do have
                        # to catch and handle all exceptions
                        Logger.major('^'*30)
                        Logger.debug("{0} threw exception:".format(execution.task))
                        execution.imprint_stack_trace()
                        Logger.error(execution.format_exception())
                        execution.fail(exception)

            reverse = list(wrappers)
            reverse.reverse()
            for wrapper in reverse:
                wrapper.after(execution, result)

            if execution.state is STATE.RUNNING:
                execution.succeed()

            # Final check of working directory: Reset it to whatever it was
            # before the Task started
            if manage_working_directory and getcwd() != previous_dir:
                # We have a set working directory, but we are not in it
                # We therefore have to change back to the working directory
                if path.isdir(previous_dir) and access(previous_dir, R_OK):
                    Logger.log("Reverting working directory back to {0}".format(previous_dir))
                    chdir(previous_dir)
                else:
                    # This is not fatal - the next Task has a chance to change
                    # it to something that does work
                    Logger.warn("Cannot change directory back to {0}- it does not exist or is not readable".format(previous_dir))

            Logger.log("{0} Time: Elapsed={1:.3f}s, internal={2:.3f}".
                        format(task, execution.duration(), execution.duration_internal()))

        except Exception as exception:  # pylint: disable-msg=W0703
            # This pathway is to handle system exceptions which would otherwise
            # unwind the stack leaving objects in a running state
            if not execution.is_complete():
                execution.system_exception(exception)
            raise

        finally:
            # Flush output buffers to ensure all std out and err associated
            # with this Task is properly captured
            Logger.major(str(execution))
            Logger.flush()

            self._pop_frame(task)
            if self.current_frame is None:
                self.last_run = execution
            Logger.debug("Leaving execute({0})".format(task.name))

        return execution

    def __str__(self):
        return "Processing {0}".format(self._pp_call_stack())


PROCESSOR = Processor()
"""Reference to the :class:`Processor` singleton"""

def build(task, handle_exceptions=False):
    """Execute one task, optionally handling exceptions.

    :param task: The task to build. Either be the name of the Task, eg
                 see :ref:`qualified-task-names`), or the function
                 reference itself.
    :type  task: function or string
    :param handle_exceptions: Default *False*. Configures how exceptions should be treated.
                              See below
    :type handle_exceptions: boolean
    :return: The :class:`Execution` call stack wrapped by a :class:`Result`
    :rtype:  :class:`Result`
    :raises: If **handle_exceptions** is *False*, :func:`build` will raise the
             Exception raised by the :class:`.Task` that failed

    **handle_exception** behaviour:

        * *False* (default): If a Task throws an exception, or fails, the
          exception is propagated to the caller.
        * *True*: The any exception thrown is handled by the function
          and the exception is wrapped in the Result object.
          The result of the call can be checked with::

              if result.success is False:
                  # do error handling
                  print result.exception

    .. warning::

        This function is for use *within a task*. Use :func:`.run` to *start*
        a build as discussed in :doc:`running`
    """
    task = task if isinstance(task, Task) else Task.find(task)
    environ['DOVETAIL_BUILD_ROOT'] = task.dir
    result = Result(PROCESSOR._execute(task))
    if not handle_exceptions and not result.success:
        raise result.exception
    return result
