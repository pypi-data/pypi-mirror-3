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

"""Command-line entry-point."""

from dovetail.util import Logger  # Load logging early to capture as much output as possible
from dovetail.loader import load, BuildModule, PackageNode
from dovetail.constants import USAGE, LICENSE, WARRANTY
from dovetail.util import InvalidTask, InvalidBuildFile, NoSuchTask, \
    CommandLineException, Terminate, tree, get_virtual_environment
from dovetail.util.utilities import  stamp_environment
from dovetail.model import Dependencies, Task, NULL_TASK
from dovetail.engine import build
from dovetail.virtual import run_virtual
from dovetail.config import REPORTS,  print_help, load_config

from sys import stderr, argv

FAILURE_BANNER = """
===============================================================================

SYSTEM ERROR while processing the following task(s): {0}

===============================================================================
"""

def validate_tasks(task_list, module=None):
    """Processes the list of Task targets into a list of normalized task names.

    The method also validates the list of tasks in the module name provided."""
    if not Task.all_tasks():
        raise InvalidTask("No tasks have been loaded")

    if isinstance(task_list, basestring):
        task_list = [ task_list ]

    try:
        for name in task_list:
            Task.find(name, module)
    except NoSuchTask as exception:
        raise InvalidTask(exception.message)

def task_help(build_file, tasks):
    """Validate arguments and attempt to print help on the tasks"""
    module = load(build_file)
    if not Task.all_tasks():
        raise InvalidBuildFile("No tasks have been loaded")

    if isinstance(tasks, basestring):
        tasks = [ tasks ]

    errors = False
    for name in tasks:
        try:
            task = Task.find(name, module)
            task.report()
        except NoSuchTask as exception:
            stderr.write(exception.message)
            stderr.write("\n")
            errors = True

    return 0 if not errors else 35

def report_tasks(module):
    """Report the tasks in the specified module in a simple one-level tree"""
    class Node(object):
        """Trivial structure to display the Task tree by Task name"""
        def __init__(self, text=None, children=None):
            self.children = [] if children is None else children
            self.text     = text

    build_module = BuildModule.find(module)
    children = [ Node(text=Task.find(task, module).report_line(full_name=False))
                        for task in build_module.tasks ]
    root = Node(children=children)
    tree(root,
         get_children=lambda x:x.children,
         node_text=lambda x:x.text,
         display_root=False)

def print_reports(result, reports):
    """Print all the reports specified in the second argument to the console on
    the Results passed as the first argument."""
    if not reports:
        return

    print
    print "="*80
    print "REPORTS"
    print
    for report_name in reports:
        print "-"*80
        report = REPORTS.lookup(report_name.upper())
        if report == REPORTS.TREE:
            result.report_tree()
        elif report == REPORTS.SLOW:
            result.report_slowest()
        elif report == REPORTS.MODULES:
            PackageNode.report_modules()
        elif report == REPORTS.DEPEND:
            BuildModule.report_load_graph()
        else: #pragma: nocover
            raise Terminate(255, "Unexpected exception: requested to print an undefined report '{0}'".format(report))

def execute_in_vm(module, tasks, reports):
    """Execute the build in the current Python VM.

    :param module:  A reference to the module of the build root
    :type  module:  sys.module
    :param tasks:   One or more tasks to run. Can be non-qualified task names
                    if they are present in build_file, or fully-qualified
                    task names for those in other files
    :type  tasks:   list of string
    :param reports: The reports to run after the build completes
    :type  reports: list of string
    :return: 0 if successful, 1 if the build failed
    :rtype:  int
    :raises: :exc:`.Terminate` if Dovetail itself crashes.
             Build steps will not raise this exception.

    .. note::

        :func:`execute_in_vm` calls :func:`.stamp_environment` to set a number
        of environment variables. These can be used by the build script to better
        understand the environment
    """
    NULL_TASK.set_logical_module(module)
    validate_tasks(tasks, module)

    # Stamp the environment with hardware, os and platform information
    stamp_environment()

    if len(tasks) == 1:
        # If only a single task, this is the root task of the build
        task = Task.find(tasks[0], module)
    else:
        # If multiple tasks specified, use a logical task as the parent
        # and add the specified tasks as dependents. We have a single-rooted
        # graph like we specify a single task.
        task = NULL_TASK
        Dependencies.add(task, *tasks)

    # Run the build
    try:
        result = build(task, handle_exceptions=True)
        Logger.set_nested(False)
        print_reports(result, reports)
        print result.banner()
        return 0 if result.success else 1
    except Exception: # pylint: disable-msg=W0703
        banner = FAILURE_BANNER.format(", ".join(tasks))
        from dovetail.util.exception import stack_trace
        stack_trace()
        raise Terminate(255, banner)

def run(tasks):
    """Used to run tasks from in a build script when the script has been
    loaded directly by Python.

    When a script is run in the following way::

        $ python build.py task1 task2

    It can invoke Dovetail functionality using this fragment::

        from dovetail import *
        import sys

        ...

        if __name__ == "__main__":
            run(sys.argv[1:])

    :param tasks:   One or more tasks to run. Can be non-qualified task names
                    if they are present in build_file, or fully-qualified
                    task names for those in other files
    :type  tasks:   list of string
    :return: 0 if successful, 1 if the build failed
    :rtype:  int
    :raises: :exc:`.Terminate` if Dovetail itself crashes.
             Build steps will not raise this exception.

    .. note::

        If you want to simply execute a task from within another task, use the
         :func:`.build` method.

    .. warning::

        Read the warnings in :doc:`running`

    """
    import sys
    #TODO: Pick up the calling module
    module = sys.modules["__main__"]
    return execute_in_vm(module, tasks, None)

###############################################################################
## Main entry point
def main(*kw):
    """Dovetail main entry point.

    Exceptions thrown due to errors in command
    line arguments or system errors are caught and an appropriate message
    and/or banner is displayed to the user rather than cryptic stack traces,
    and Dovetail exits the Python interpreter."""

    def inner(*kw):
        """A simple entry-point to Dovetail taking a list of command-line arguments,
        and errors in operation are thrown as exceptions.

        Errors in the command line cause this function to raise an Exception which
        the caller should catch. Also, system exceptions thrown in the processing
        of the build are propagated out of this function (this does not include
        exceptions raised in Tasks, which are explicitly handled)."""
        args = load_config(kw)

        # Interpret the command line arguments
        if args.license:
            print LICENSE
            result = 0
        elif args.warranty:
            print WARRANTY
            result = 0
        elif args.usage:
            print USAGE
            result = 0
        elif args.help:
            if args.task:
                result = task_help(args.build_file, args.task)
            else:
                print_help()
                result = 0
        elif not args.task:
            module = load(args.build_file)
            if Task.all_tasks():
                print "The following Tasks are available in {0}:".format(args.build_file)
                report_tasks(module)
            else:
                print "No tasks have been loaded from {0}".format(args.build_file)
            result = 32
        elif args.virtualenv:
            result = run_virtual(args.virtualenv, args.clear, kw)
        else:
            module = load(args.build_file)
            result = execute_in_vm(module, args.task, args.reports)

        return result


    if not kw:
        kw = argv[1:]
    try:
        if get_virtual_environment():
            Logger.debug("Dovetail virtual environment slave starting")
        result = inner(*kw)

        if get_virtual_environment():
            what = "Dovetail slave"
        else:
            what = "Dovetail"
        if result is None or result == 0:
            msg = "has completed successfully"
        else:
            msg = "has completed with errors: Returning {0}".format(result)
        Logger.debug("{0} {1}".format(what, msg))
        exit(result)
    except CommandLineException as exception:
        if not exception.return_code:
            if exception.message is not None:
                print exception.message
        else:
            if exception.message is not None:
                stderr.write(str(exception.message))
                stderr.write("\n")
                stderr.write(exception.additional_help())
                stderr.write("\n")
        exit(exception.return_code)

if __name__ == "__main__":
    main()
