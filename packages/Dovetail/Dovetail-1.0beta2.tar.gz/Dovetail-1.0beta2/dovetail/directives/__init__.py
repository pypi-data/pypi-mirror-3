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

"""This package contains the Dovetail's core 'language' and markup
for build scripts.

Directives
..........

Fundamental directives for declaring Tasks, dependencies and conditions to
execute a Task:

+----------+------------------------+-----------------------------------------------------------------+
| Name     | Parameters             | Description                                                     |
+==========+========================+=================================================================+
| :func:`\ | *none*                 | Declares a function to be a build :class:`dovetail.model.Task`. |
| .task`   |                        | Once declared, the Task can be referenced either by passing a   |
|          |                        | reference to the function itself, or by it's name.              |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | 1 or more Task names   |                                                                 |
| .depends`| or function references | Declares that a Task is dependent on another Task.              |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | 1 or more predicates   | Executes a Task if predicate returns *True*, otherwise          |
| .do_if`  |                        | Task is skipped.                                                |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | 1 or more predicates   | Skips a Tasks if predicate returns *True*, otherwise            |
| .skip_if`|                        | Task is executed                                                |
+----------+------------------------+-----------------------------------------------------------------+

This collection of directives allow the build engineer to fail a build when
specific conditions occur:

+------------------+----------------+-----------------------------------------------------------------+
| Name             | Parameters     | Description                                                     |
+==================+================+=================================================================+
| :func:`\         | 1 or more      | Fails the task if the predicate returns *True*. @fail_if is     |
| .fail_if`        | predicates     | evaluated *after* the Task has otherwise completed.             |
|                  |                | This is often combined with the following predicates:           |
|                  |                |                                                                 |
|                  |                | * :class:`.ResultEquals`                                        |
|                  |                | * :class:`.ResultNone`                                          |
|                  |                | * :class:`.ResultZero`                                          |
|                  |                | * :class:`.Installed`                                           |
|                  |                | * :class:`.engine.StdErr`                                       |
+------------------+----------------+-----------------------------------------------------------------+
| :func:`\         | *none*         | Fails the task if the task was skipped, eg by @skip_if or       |
| .fail_if_skipped`|                | @do_if. This can be useful if there are several @skip_if and/or |
|                  |                | @do_if predicates and you need to ensure that at least one      |
|                  |                | allowed the task to execute                                     |
+------------------+----------------+-----------------------------------------------------------------+
| :func:`\         | *none*         | Checks the return value of the task for Unix process semantics, |
| .check_result`   |                | failing the task if the result is non-null and non-zero         |
+------------------+----------------+-----------------------------------------------------------------+


Directives that modify the execution environment of the Task:

+----------+------------------------+-----------------------------------------------------------------+
| Name     | Parameters             | Description                                                     |
+==========+========================+=================================================================+
| :func:`\ | :ref:`\                | Modifies the :data:`os.environ` for the duration of the Task    |
| .adjust\ | environment_arguments` | and its dependents                                              |
| _env`    |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | directory              | Changes the current working directory to the nominated location |
| .cwd`    |                        | before the task runs. This is reverted after the task is        |
|          |                        | complete.                                                       |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | 1 or more directories  | Ensure that the directories exist, making them if not           |
| .mkdirs` |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :func:`\ | 1 or more package      | Ensure that the Python packages are present, installing if      |
| .requ\   | requirements           | necessary.                                                      |
| ires`    |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+

Predicates
..........

Predicates are logical statements used to determine when a Task executes, is
skipped or should be failed. Predicates are used by:

    * ``@do_if``
    * ``@skip_if``
    * ``@fail_if``

A Predicate is a Callable which will be evaluated during the build
and returns a boolean.

Predicates that test the :data:`os.environ`:

+----------+------------------------+-----------------------------------------------------------------+
| Name     | Parameters             | Description                                                     |
+==========+========================+=================================================================+
| :class:`\| :ref:`\                | Test whether environment variables are set, or have a specific  |
| .Env`    | environment_arguments` | value                                                           |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| 1 or more NAME="regex" | Test whether environment variables are match the supplied       |
| .EnvRE`  |                        | regular expressions                                             |
+----------+------------------------+-----------------------------------------------------------------+

Predicates that test the file system:

+----------+------------------------+-----------------------------------------------------------------+
| Name     | Parameters             | Description                                                     |
+==========+========================+=================================================================+
| :class:`\| path, mode             | Test is a path has certain mode flags. Wrapper to               |
| .Access` |                        | :func:`os.access`. Note: On Windows, only os.R_OK is respected  |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| path                   | Tests if the path is a directory.                               |
| .IsDir`  |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| path                   | Tests if the path is a normal file                              |
| .IsFile` |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| path                   | Tests if the path is a link                                     |
| .IsLink` |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| path                   | Tests if the path is a mount-point (disk).                      |
| .IsMount`|                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| path, size             | Tests if the file pointed to by *path* is larger than *size*    |
| .Larger\ |                        | bytes                                                           |
| Than`    |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| source iterator,       | Tests if *any* file in the source iterator is newer than *any*  |
| .Newer`  | target iterator        | files in the target iterator. Useful if you want to skip a      |
|          |                        | Task if nothing has changed. Often used in conjunction with     |
|          |                        | :class:`Glob` or `Formic <http://www.aviser.asia/formic>`_      |
+----------+------------------------+-----------------------------------------------------------------+

Predicates for testing whether a package or executable is present:

+----------+------------------------+-----------------------------------------------------------------+
| Name     | Parameters             | Description                                                     |
+==========+========================+=================================================================+
| :class:`\| requirement            | Tests if the :program:`easy_install`-like requirements are      |
| .Instal\ | specifications         | present.                                                        |
| led`     |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+
| :class:`\| executable_name        | Tests if the named executable is on the path.                   |
| .Which`  |                        |                                                                 |
+----------+------------------------+-----------------------------------------------------------------+

Predicates to test a Task's result:

+--------------------+------------------------+-----------------------------------------------------------------+
| Name               | Parameters             | Description                                                     |
+====================+========================+=================================================================+
| :class:`\          | *None*                 | True if the current Task sent any output to :data:`sys.stderr`  |
| .engine.StdErr`    |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | value                  | True if the return value from the Task function equals the      |
| .ResultEquals`     |                        | supplied argument                                               |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the return value from the Task function equals is *None*|
| .ResultNone`       |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the return value from the Task function is 0            |
| .ResultZero`       |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+


Predicates to test the processing state of the Dovetail build engine:

+--------------------+------------------------+-----------------------------------------------------------------+
| Name               | Parameters             | Description                                                     |
+====================+========================+=================================================================+
| :class:`.Depend\   | *None*                 | True if the current Task has at least one dependent Task that   |
| entSucceeded`      |                        | succeeded. False if there are no subtasks                       |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task has been aborted (dependent failed)    |
| .StateAborted`     |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task has failed                             |
| .StateFailed`      |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task has already been executed successfully |
| .StateRepeated`    |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task was skipped                            |
| .StateSkipped`     |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task has started but not yet finished or    |
| .StateStarted`     |                        | failed.                                                         |
+--------------------+------------------------+-----------------------------------------------------------------+
| :class:`\          | *None*                 | True if the current Task has succeeded                          |
| .StateSucceeded`   |                        |                                                                 |
+--------------------+------------------------+-----------------------------------------------------------------+

Logic
.....

A number of Task decorators take Predicates as arguments; if the decorator
takes multiple predicates they will be 'anded' together - *True* only if all
predicates are *True*.

Predicates can be combined into arbitrary logical statements using logical
operator predicates:

+----------+---------------+------------------------------------------------+
| Operator | Predicate     | Description                                    |
+==========+===============+================================================+
| **OR**   | :class:`.Any` | True iff *any* predicate is True               |
+----------+---------------+------------------------------------------------+
| **AND**  | :class:`.All` | True iff *all* predicates are True             |
+----------+---------------+------------------------------------------------+
| **NOT**  | :class:`.Not` | The negation of the single predicate argument  |
+----------+---------------+------------------------------------------------+

(**iff** stands for 'if and only if')

By combining these operators, you can make constructions like::

    Not(Any(p1, p2, All(p3, p4)))

.. _environment_arguments:

Environment definition arguments
................................

Environment definitions are used by:

    * The :class:`Env` predicate, and
    * The :func:`adjust_env` directive

Several methods use the **\*args** and **\*\*kwargs** argument magic to tersely
specify:

    * Tests to environment, such as whether a specific environment variable
      is set, or has a specific value
    * Modifications to the environment, so environment variables can be set,
      modified or unset.

The **\*args** section represents *set* or *unset* variables (either tests that
a variable is set, or unsets a variable)::

        Env('BASH')               # True if environment variable $BASH is set
        Env('BASH', 'HOSTNAME')   # True if $BASH and $HOSTNAME are both set
        @adjust_env('A')          # Unsets $A
        @adjust_env('A', 'B')     # Unsets $A and $B

The **\*\*kwargs** represents the *value* of a specific environment variable::

        Env(DOVETAIL_NODE='pluto.example.com')   # Run only on the pluto build machine
        @adjust_env(A="new")                     # Sets $A=new

**\*args** and **\*\*kwargs** can be combined::

        Env('BASH', DOVETAIL_NODE='pluto.example.com')

And finally, a **\*\*kwargs** argument with a value of *None* is exactly the
same as a **\*args** entry. The following have identical behavior::

        Env('BASH')
        Env(BASH=None)

.. _modification_dictionary:

Modification dictionary
.......................

Modification dictionaries are used by:

    * :func:`.apply_environment`
    * :func:`.pp_adjust_env`

This is a dictionary that is used to record or make changes to another
dictionary, the target. It may:

    * Create new entries
    * Overwrite an existing entry
    * Delete an entry (a key)

The entries in the modification dictionary have the following semantics

    * **Has value**: the modification will either *set* or
      *overwrite* the entry with the same key in the target dictionary
    * **No value**: the modification will *delete* any entry with the
      same key in the target dictionary

Keys in the target not matched by an entry in the modification dictionary
will not be modified.

"""

from dovetail.directives.core import check_result, depends, task, \
    fail_if_skipped, do_if, skip_if, fail_if, Any, All, Not

from dovetail.directives.engine import \
    StdErr, StateStarted, StateSkipped, StateFailed, \
    StateAborted, StateRepeated, StateSucceeded, \
    ResultNone, ResultZero, ResultEquals, \
    DependentSucceeded

from dovetail.directives.environment import adjust_env, Env, EnvRE

from dovetail.directives.files import cwd, mkdirs, \
    Access, IsFile, IsDir, IsLink, IsMount, \
    LargerThan, Which, Newer, Glob

from dovetail.directives.packages import Installed, requires, install
