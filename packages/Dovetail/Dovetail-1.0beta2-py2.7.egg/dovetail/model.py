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

"""The object model for Dovetail."""

from dovetail.util import NoSuchTask, Logger, tree
from dovetail.util.trim import trim
from dovetail.loader import BuildModule

from os import path
from types import FunctionType

NOT_LOADED = "Task.find('{0}') was not called from a file loaded by Dovetail. \
Did you use dovetail.load()?"

class TaskWrapper(object):
    """TaskWrappers are abstractions of directives that have been applied
    to a Task, eg @adjust_env().

    A few directives are implemented directly in the Dovetail :class:`.Processor`
    and are not present as :class:`TaskWrapper` instances:

        * @task
        * @depends
        * @cwd

    Directive implementation contains a pre-Task function or a post-Task
    function or both. The pre- and post-Task functions may interrogate the
    environment, modify it, perform any calculation or modify the state of
    execution (eg by calling :meth:`.Execution.skip` or :meth:`.Execution.fail`)

    :param name:   Task name
    :type  name:   string
    :param func:   The Function that underlies a Task. Mandatory
    :type func:    function()
    :param before: Default *None*. Function called before the Task and Dependencies
                   Return result ignored.
    :type before:  function(:class:`Execution`)
    :param after:  Default *None*. Function called after the Task and Dependencies.
                   Second argument, result, will be the return value from
                   the Task or *None*. The return result ignored by Dovetail.
    :type after:   function(:class:`Execution`, result)

    """
    WRAPPERS = {}

    @staticmethod
    def decorator_maker(name, before=None, after=None):
        """Allows a directive with arguments to register its pre- and post-
        functions.

        This method returns a decorator which uses by :meth:`TaskWrapper.decorate`.

        :param name:   Name of the :class:`Task` to wrap
        :type  name:   string
        :param before: Default *None*. Function called before the Task and Dependencies
                       Return result ignored.
        :type before:  function(:class:`Execution`)
        :param after:  Default *None*. Function called after the Task and Dependencies.
                       Second argument, result, will be the return value from
                       the Task or *None*. The return result ignored by Dovetail.
        :type after:   function(:class:`Execution`, result)
        :return: A decorator of the :class:`TaskWrapper`
        :rtype:  function(function)
        """
        def decorator(f):
            """Returns a decorated function, wrapping it with the before() and
            after functions in decorate_maker"""
            return TaskWrapper.decorate(name, f, before, after)
        return decorator

    @staticmethod
    def decorate(name, func, before=None, after=None):
        """Allows a zero-argument directive to register its pre- and post-
        functions.

        :param func:   The function (:class:`Task`) being decorated by the directive
        :type  func:   function()
        :param before: Default *None*. Function called before the Task and Dependencies
                       Return result ignored.
        :type before:  function(:class:`Execution`)
        :param after:  Default *None*. Function called after the Task and Dependencies.
                       Second argument, result, will be the return value from
                       the Task or *None*. The return result ignored by Dovetail.
        :type after:   function(:class:`Execution`, result)
        :return: func
        :rtype:  function()

        .. Note::

            This method has the important side-effect that it creates and
            registers a :class:`TaskWrapper` that will be used by the Dovetail
            engine
        """
        wrapper = TaskWrapper(name, func, before, after)
        Logger.debug("Registered {0}".format(wrapper))
        return func

    def __init__(self, name, func, before, after):
        """Creates a TaskWrapper of a given name."""
        # Note - this can be called BEFORE the task is instantiated
        assert name    is not None and isinstance(name, basestring)
        assert func    is not None and hasattr(func,   '__call__')
        assert before  is     None or  hasattr(before, '__call__')
        assert after   is     None or  hasattr(after,  '__call__')
        assert before or after
        self._name      = name
        self._task_name = Task.as_task_name(func)
        self._before    = before
        self._after     = after

        try:
            TaskWrapper.WRAPPERS[self._task_name].append(self)
        except KeyError:
            TaskWrapper.WRAPPERS[self._task_name] = [ self ]

    @staticmethod
    def get(task):
        """Gets a list of TaskWrappers for this Task.

        :param task: A Task
        :type  task: :class:`Task`
        :return: The TaskWrappers for task
        :rtype: list of :class:`Task`
        """
        assert task is not None
        assert isinstance(task, Task)
        try:
            return TaskWrapper.WRAPPERS[task.name]
        except KeyError:
            # Add the result so future looks are quicker
            new = []
            TaskWrapper.WRAPPERS[task.name] = new
            return new

    def before(self, execution):
        """Executes the **before()** method of the wrapper (if any)"""
        if self._before:
            Logger.debug("{0}: before()".format(self))
            return self._before(execution)

    def after(self, execution, result):
        """Executes the **after()** method of the wrapper (if any)"""
        if self._after:
            Logger.debug("{0}: after()".format(self))
            return self._after(execution, result)

    def __str__(self):
        return "Directive {0} on {1}".format( self._name, self._task_name)


class Dependencies(object):
    """A simple dictionary-based store for recording dependencies of one
    :class:`Task` on another.

    This is an internal object used by the :func:`.depends` directive
    and the :class:`Task` class.

    This class does *not* handle automatic dependencies (see
    :ref:`automatic-dependencies`).
    """
    # An index of task->dependencies where
    #  * Task is a fully qualified name relative to the build root
    #  * Dependencies is a list of Tasks _relative_ to the key
    _index = {}

    @staticmethod
    def add(task_or_func, *dependencies):
        """Adds a list of dependencies to a Task.

        :param task_or_func: A task defined either by name or by its function
        :type  task_or_func: :class:`Task` or string
        :param dependencies: The dependant tasks defined by name or function
        :type  dependencies: list of function or string
        """
        assert task_or_func is not None
        if isinstance(task_or_func, Task):
            task_name = task_or_func.name
        else:
            assert type(task_or_func) is FunctionType
            task_name = Task.as_task_name(task_or_func)

        Dependencies._index[task_name] = dependencies

    @staticmethod
    def get(task):
        """Retrieves a task's dependencies.

        :param task: The task for which dependencies are sought
        :type  task: :class:`Task`
        :return:     list of dependencies for a Task, or the empty list if none.
        :rtype:      list of function or string
        """
        assert task is not None
        assert isinstance(task, Task)
        try:
            return Dependencies._index[task.name]
        except KeyError:
            return []


class TaskWorkingDirectories(object):
    """A simple dictionary for storing @cwd directive working directory values
    and their retrieval.

    This class is necessary as the Task has not been fully created when the
    @cwd decorator is executed.

    See Task.get_working_directory() for more details"""
    _index = {}

    @staticmethod
    def set(task_or_func, directory):
        """Sets a working directory value for a specific Task.

        Working directories may be declared by Task instance or by
        their function"""
        assert task_or_func is not None
        if isinstance(task_or_func, Task):
            task_name = task_or_func.name
        else:
            assert type(task_or_func) is FunctionType
            task_name = Task.as_task_name(task_or_func)

        Logger.debug("Setting working directory for {0} to {1}".format(task_name, directory))
        TaskWorkingDirectories._index[task_name] = directory

    @staticmethod
    def get(task):
        """Retrieves the working directory set by @cwd for a Task; if not
        present, it throws KeyError"""
        assert task is not None
        assert isinstance(task, Task)
        return TaskWorkingDirectories._index[task.name]

def null():
    """The function used to create the :class:`NullTask` held in :data:`dovetail.model.NULL_TASK`"""
    pass


class Task(object):
    """An object representing a Task in a build system.

    Tasks are functions, taking no arguments, identified with the
    '\@task' directive. A task's short name is the name of the function.
    A hello-world for Dovetail is::

        from dovetail import task

        @task
        def hello_world():
            pass

    :param func: A reference to the task's function
    :type  func: function()

    Tasks have the following members:

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | module       | module               | The module in which the Task function is |
    |              |                      | declared                                 |
    +--------------+----------------------+------------------------------------------+
    | func_name    | string               | The name of the function (**f.__name__**)|
    +--------------+----------------------+------------------------------------------+
    | name         | string               | The fully qualified name of the Task     |
    +--------------+----------------------+------------------------------------------+
    | source       | string               | The absolute path of the file in which   |
    |              |                      | the Task is declared                     |
    +--------------+----------------------+------------------------------------------+
    | dir          | string               | The directory in which source is situated|
    +--------------+----------------------+------------------------------------------+

    At instantiation time, the task instance captures the *name* and *module*
    of the task's function - it does *not* capture a reference to the function.
    This approach means the function can be decorated or otherwise modified
    after the @task decorator is processed and the  :class:`Task` instance
    will 'see' the additional decoration.

    At the time of resolution in :meth:`get_function`, the module's
    namespace is interrogated for the function name.

    A task (in the build sense) is modelled by a combination of classes:

    +-----------------------+--------------------------------------------------+
    | Class                 | Description                                      |
    +=======================+==================================================+
    | :class:`Task`         | The class models the core aspects of a task and  |
    |                       | provides a in-memory datastore for all tasks.    |
    +-----------------------+--------------------------------------------------+
    | :class:`TaskWrapper`  | A algorithmic class that captures the wrapping   |
    |                       | behaviour of directives such as @Env and @do_if  |
    +-----------------------+--------------------------------------------------+
    | :class:`Dependencies` | A data store capturing all the dependencies of   |
    |                       | every task loaded. Dependencies are not resolved |
    |                       | until runtime to allow forward references in     |
    |                       | build files. The class provides an API to look   |
    |                       | up any task's dependencies.                      |
    +-----------------------+--------------------------------------------------+
    | :class:`TaskWorking\  | A data store capturing the path specified in the |
    | Directories`          | @cwd directive. This is needed because the Task  |
    |                       | has not been created when the @cwd directive is  |
    |                       | processed.                                       |
    +-----------------------+--------------------------------------------------+

    Implementation note: There is a special Null Task always present that is
    used to to logically root a graph of Tasks. This can be retrieved
    from :data:`dovetail.model.NULL_TASK`.
    """
    _tasks = {}

    def __init__(self, func):
        assert func is not None
        assert type(func) is FunctionType
        from sys import modules
        self.module    = modules[func.__module__]
        self.func_name = func.__name__
        self.name      = Task.as_task_name(func)
        self.source    = path.abspath(self.module.__file__)
        self.dir       = path.dirname(self.source)
        self._working  = None

        # Register this Task in global database of Tasks using the full name
        Task._tasks[self.name]  = self

    @staticmethod
    def as_task_name(func):
        """A utility to create a Task name for a function.

        :param func: The function
        :type  func: function()
        :return:     Task name. The name is typically of the form "module:function",
                     but module name is dropped for the :mod:`__main__` module
        :rtype:      string
        """
        return func.__module__ + ":" + func.__name__

    @staticmethod
    def find(name_or_function, module=None):
        """Return the Task instance for the task of this name or function.

        The Task can be looked up by passing a function reference - this is
        the easiest approach. You can also look up by Task name, which is
        relative to the package you are in. Tasks in the same file have the
        same name as the function. Otherwise Tasks declared at or below this
        use a relative package naming scheme, eg "package:function_name" -
        see :ref:`qualified-task-names`

        The module argument can be specified to determine the starting point
        of the relative name search. If *None*, the call stack is examined to
        start the search from the file highest on the stack loaded by
        :func:`dovetail.load`.

        :param name_or_function: The name of the :class:`Task` or the
                                 :class:`Task` name
        :type  name_or_function: function() or string
        :param module:           Default *None*. Optional :class:`module` to
                                 guide the search for the task.
        :type  module:           module
        :return:                 The requested :class:`Task`
        :rtype:                  :class:`Task`
        :raises:                 :exc:`.NoSuchTask`

        .. Note ::

            1. If using the **module** argument, only use the **short** name
               for the task
            2. If the task is specified by *function*, the **module** argument
               is ignored
        """
        if isinstance(name_or_function, basestring):
            if module:
                build_module = BuildModule.find(module)
            else:
                build_module = BuildModule.current()
                if build_module is None:
                    raise NoSuchTask(NOT_LOADED.format(name_or_function))
            return build_module.find_task(name_or_function)
        elif hasattr(name_or_function, "__call__"):
            # Function or callable, so fully qualified and 'simple'
            name = Task.as_task_name(name_or_function)
            try:
                return Task._tasks[name]
            except KeyError:
                raise NoSuchTask("Function {0} in has not been registered as a Task. Did you decorate with @task?".
                                      format(name_or_function))
        else:
            raise NoSuchTask("Cannot look up Task '{0}': Value is not a string or a function".format(name_or_function))

    @staticmethod
    def all_tasks():
        """Returns a set of all :class:`Task` instances known to Dovetail."""
        return { task for task in Task._tasks.itervalues()
                            if not isinstance(task, NullTask)}

    def get_function(self):
        """Returns the function implementing this task.

        This is looked up by name within the module namespace at the point
        of request.
        """
        return vars(self.module)[self.func_name]

    def get_wrappers(self):
        """Returns the :class:`TaskWrapper` instances associated with this Task.

        :return: The directives
        :rtype:  list of :class:`TaskWrapper`
        """
        return TaskWrapper.get(self)

    def get_doc(self):
        """Gets the :class:`Task` instance's documentation string.

        :return: The reformatted docstring from the Task's implementation
        :rtype:  string"""
        func = self.get_function()
        return trim(func.__doc__)

    def get_working_directory(self):
        """Returns the directory in which the Task wants to be run.

        :return: The :class:`Task`'s working directory
        :rtype:  string

        This defaults to the :attr:`Task.dir`, but can be set directly. The working
        directory has several levels of default, in this order:

            1) Value set using :class:`TaskWorkingDirectories` or
               the :func:`cwd` directive
            2) :attr:`Task.dir`

        If :class:`TaskWorkingDirectories` or :func:`cwd` explicitly sets the
        working directory to *None* (eg **@cwd(None)**), then the the Dovetail engine
        switches of working directory functionality for this task, and the task
        will execute in the working directory of the calling task.
        """
        try:
            directory = TaskWorkingDirectories.get(self)
            if directory is None or path.isabs(directory):
                return directory
            return path.join(self.dir, directory)
        except KeyError:
            return self.dir

    def build_dep_tree(self):
        """Builds out a tree of Task dependencies for reporting.

        :return: A directed graph of :class:`Task` dependencies
        :rtype:  :class:`Node`

        +--------------+----------------------+----------------------------------+
        | **Node Class**                                                         |
        +--------------+----------------------+----------------------------------+
        | Attribute    | Type                 | Description                      |
        +==============+======================+==================================+
        | task         | function() or string | The :class:`Task`                |
        +--------------+----------------------+----------------------------------+
        | children     | list of function()   | Dependencies of the :attr:`task` |
        |              | or string            |                                  |
        +--------------+----------------------+----------------------------------+
        """
        class Node:
            """A simple data-holder for a Task and its children"""
            def __init__(self, task):
                self.task = task
                self.children = []
        node = Node(self)
        for task in self.dependencies():
            node.children.append(task.build_dep_tree())
        return node

    def report_line(self, full_name=True):
        """Writes one line in the Task report report - the Task name
        and docstring"""
        doc = self.get_doc()
        name = self.name if full_name else self.func_name
        if doc is None:
            return name
        else:
            return "{0}\n{1}".format(name, doc)

    def report(self):
        """Prints a report of this Task and all its children, recursively;
        each Task's docstring is printed"""
        nodes = self.build_dep_tree()
        tree(nodes, get_children=lambda x: x.children, node_text=lambda x: x.task.report_line())

    def dependencies(self):
        """Returns a list of Task instances on which this Task depends.

        Returned dependencies include both the explicit dependencies
        created by @depends and stored in :class:`Dependencies`, and
        also automatic dependencies between tasks of the same name in
        different files (see :ref:`automatic-dependencies`).

        This is an abstract method implemented in:

            * :meth:`LoadedTask.dependencies`
            * :meth:`NullTask.dependencies`
        """
        pass

    def __str__(self):
        return "Task {0}".format(self.name)


class NullTask(Task):
    """A logical root of the Task dependency hierarchy when the user specifies
    multiple Tasks from the command line. This allows the Task graph to be
    logically single-rooted.

    This object is stored in :data:`dovetail.model.NULL_TASK`"""
    def __init__(self):
        Task.__init__(self, null)
        self.logical_module = None

    def set_logical_module(self, module):
        """Called to anchor the Null Task as logically associated with the
        build file specified on the command line.

        This is needed so that children of the NullTask have a build root."""
        self.logical_module = module

    def dependencies(self):
        """Returns a list of Task instances on which this Task depends.

        This includes tasks of the same name in child modules
        """
        dep = [ self.find(dependent, self.logical_module) for dependent in Dependencies.get(self)]
        return dep

    def __repr__(self):
        return "NullTask singleton"


class LoadedTask(Task):
    """A minor specialization of Task that registers with BuildModule so
    that its dependencies can be resolved."""
    def __init__(self, func):
        Task.__init__(self, func)
        # Register the Task with the BuildModule for automatic
        # dependency generation
        BuildModule.register_task(self)

    def dependencies(self):
        """Gets this task's dependencies.

        :return: The :class:`Task` instances on which this instance depends.
                 If no dependencies, it will be the empty list
        :rtype:  list of :class:`Task`

        .. Note::

            This method returns the tasks of the same name in child build modules.
        """
        dep = [ self.find(dependent, self.module) for dependent in Dependencies.get(self)]

        build_module = BuildModule.find(self.module)
        auto = build_module.get_child_tasks_with_name(self.func_name)
        modules = [ task.module.__name__ for task in auto ]
        if modules:
            Logger.log("Found {0} in following child modules:\n{1}".format(self.func_name, ", ".join(modules)))
        dep.extend(auto)

        return dep

    def __repr__(self):
        return "Task {0}".format(self.name)

# Initialise the null task
NULL_TASK = NullTask()
"""A reference to the :class:`NullTask` singleton"""