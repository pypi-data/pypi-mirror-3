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

"""Dovetail API implementation.

.. _class_relationship:

Class-relationship diagram
--------------------------

::

              Module: loader.py                            Module: model.py

                            build file                                 +--------------+
    +-------------+       +-------------+        +-------------+       | Dependencies |
    |             |------>|             |<------*|             |       +--------------+
    | PackageNode |       | BuildModule |        |    Task     |
    |             |*-+    |             |*-+     |             |       +--------------+
    +-------------+  |    +-------------+  |     +-------------+       | TaskWrapper  |
                 \___/                 \___/            ^              +--------------+
                Package                 Loaded          |
               Structure                                |           Objects in model.py are related
                                                        |           but look each other up dynamically
                                                        *
                                                 +--------------+
                                                 |              |
               +-------------+ <<creates>>       |  Execution   |
               |             |~~~~~~~~~~~~~~~~~~>|              |*-+
               |             |                   +--------------+  |
               |  Processor  |                          ^      \___/
               |             |                          |
               |             | <<creates>>       +--------------+
               |             |~~~~~~~~~~~~~~~~~~>|              |
               +-------------+                   |    Result    |
                                                 |              |
                                                 +--------------+

                              Module: engine.py

Links:

    * :class:`.PackageNode`: Model of package/directory structure of the build files
    * :class:`.BuildModule`: Models build files
    * :class:`.Task`: Model of a Task
        * :class:`.Dependencies`: Stores dependencies between Tasks
        * :class:`.TaskWrapper`: Directives (such as ``@do_if`` or ``@adjust_env``)
    * :class:`.Processor`: The class that runs the build
        * :class:`.Execution`: The running and completed state of the build
        * :class:`.Result`: Container for a build's result

.. _flow_of_events:

Flow of events
--------------

The major flow of events when running within the same Python VM::

    .   main.py        .   loader.py   .   engine.py                               .
    .                  .               .                                           .
    . +-------------+  .               .                                           .
    . |    main()   |  .               .                                           .
    . +-------------+  .               .                                           .
    .        |         .               .                                           .
    .        v         .               .                                           .
    . +-------------+  .   +--------+ This instantiates the                        .
    . |   inner()   |----->| load() | PackageNode, BuildModule                     .
    . +-------------+  .   +--------+ and Task objects                             .
    .        |         .               .                                           .
    .        v         .               .                                           .
    . +-------------+  .               .                                           .
    . | execute_in_ |  .               .  +---------+    +----------------------+  .
    . |    vm()     |-------------------->| build() |--->| Processor._execute() |  .
    . +-------------+  .               .  +---------+    +----------------------+  .
    .                  .               .                                           .

Links:

    * :func:`.main`: Entry point from the command line
    * :func:`.load`: Loads build files creating:
        * :class:`.PackageNode`: Models the packages
        * :class:`.BuildModule`: Models build files
        * :class:`.Task`: Task instances (and other associated structures)
    * :func:`.build`: Runs the build


.. Note::

    :func:`.execute_in_vm` calls :func:`.stamp_environment` to set a number
    of environment variables before the call to :func:`.build`

.. _processor-execute:

Processor._execute implementation
---------------------------------

The :class:`.Processor` 'runs' a build using the following algorithm to
execute a single :class:`.Task`, recording activity in :class:`.Execution`
instances on a stack. The :class:`.Execution` states are defined in the
Enumeration :data:`dovetail.engine.STATE`:

    * Method **Processor._execute(self, task)**:

        1. **Begin**: Push a new :class:`.Execution` frame onto the stack

        2. **Check for errors**:

            2.1. Check if we have already run this task. If update the frame to STATE.REPEATED
               and go to #10

            2.2. Check if there is a circular invocation which has lead to
               an infinite recursion. If so, fail the build and go to #10

        3. **CWD**: Change working directory unless specifically disabled with
           ``@cwd(None)``

        4. **Directives**: Execute the :meth:`.TaskWrapper.before` method of
           all directives

        5. **Dependencies**: If :attr:`Execution.state` is not STATE.SKIPPED or STATE.FAILED:

            5.1. Loop over :meth:`.Task.dependencies`

                5.1.1. Recursive call to **Processor._execute()** to execute the :class:`.Task`.
                       If the execution was not successful (:meth:`.Execution.is_ok` is *False*),
                       fail this :class:`.Task` with STATE.ABORT and go to #8

        6. **CWD**: Check the working directory to ensure that anything the dependents did
           is reverted here before the main body of the :class:`.Task` runs

        7. **Body**: Execute the :class:`.Task` body by execute the function returned by
           :meth:`.Task.get_function()`

        8. **Directives**: Execute the :meth:`.TaskWrapper.after` method of all
           directives *in reverse order*

        9. If nothing went wrong, mark this :class:`.Execution` with STATE.SUCCEEDED

        10. **CWD**: Reset the working directory

        11. **End**: Pop the :class:`.Execution` stack frame

This method is heavily error-trapped and guarded - in the event that any failures
occur in the directives (in the :meth:`.TaskWrapper.before` and
:meth:`.TaskWrapper.after` methods) or the task dependencies or the task's function,
the method will catch the error and fail gracefully and safely.

.. Note::

    Exceptions raised during this process can trigger two different outcomes:

        1. If the exception occurs executing a :class:`.Task` function, then the
           :class:`.Task` is failed (STATE.FAIL), and the build is failed

        2. Otherwise, the exception must have come from the Dovetail framework, so
           the exception is propagated up the the highest level as a system failure.

"""

# Core model and APIs
from dovetail.loader import load, is_loaded
from dovetail.model import Task, NULL_TASK
from dovetail.engine import build, Execution, Result, STATE

# All directives
from dovetail.directives import *

# All exported Utilities
from dovetail.util import *

# the 'main' method
from dovetail.main import run

# Flag determining if this is a virtualenv slave
from dovetail.util import get_virtual_environment

if not is_loaded():
    from dovetail.loader import load_from_import
    load_from_import()
