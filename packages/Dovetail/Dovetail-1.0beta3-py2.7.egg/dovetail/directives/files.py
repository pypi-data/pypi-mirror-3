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

"""Predicates and directives for the file system."""

# Suppress checking of unused parameters - the classes/functions implement an
# interface and don't need all the arguments.
# pylint: disable-msg=W0613
# The classes in this file are deliberately simple
# pylint: disable-msg=R0903

from dovetail.util import Logger
from dovetail.util.which import which
from dovetail.model import TaskWrapper, TaskWorkingDirectories

import os

def mkdirs(*required_dirs):
    """Ensures that the give path(s) are present before the decorated function is called, creating if necessary.

    :param required_dirs: A number of paths. For each path that does not exist,
                          :func:`os.makedirs` is called to create it
    :type required_dirs: string
    """
    #noinspection PyUnusedLocal
    def before(execution):
        for required_dir in required_dirs:
            if os.path.exists(required_dir):
                Logger.log("@mkdirs: Directory {0} exists".format(required_dir))
            else:
                Logger.major("@mkdirs: Making directory {0}".format(required_dir))
                os.makedirs(required_dir)
    return TaskWrapper.decorator_maker("@mkdirs", before=before)


def cwd(directory):
    """The wrapped Task will be run in the specified working directory, and the
    current working directory restored on completion.

    :param directory: The directory to run the Task in; if *None*, Dovetail
                      will not set _any_ directory for this Task, but leave
                      the Task in the most recently set directory.
    :type directory:  string

    *Implementation note*: :func:`cwd` uses the :meth:`.TaskWorkingDirectories.set`
    method to store the preferred directory."""
    def cwd_wrapper(f):
        """Wrapper function required by the decorator idiom"""
        TaskWorkingDirectories.set(f, directory)
        return f
    return cwd_wrapper


class Which(object):
    """A predicate for testing whether an executable is present or on the path.

    :param executable_name: The file (base) name to look for
    :type  executable_name: string
    :rtype: boolean

    Uses a Python implementation of the Unix :obj:`which` command: :func:`dovetail.util.which.which`"""
    def __init__(self, executable_name):
        self.executable_name = executable_name
        #: :type: string

    def __call__(self):
        location = which(self.executable_name)
        if location is None:
            return False
        else:
            Logger.log("Which: Found {0}".format(location))
            return True

    def __str__(self):
        return "which({0})".format(self.executable_name)


class Access(object):
    """A predicate version of :func:`os.access`.

    .. warning:

        Windows respects only the os.R_OK flag.

    :param path: The path to test
    :type  path: string
    :param mode: Same semantics and values as :func:`os.access`:
    :type  mode: int
    :return: Same as: :obj:`os.access(path, mode)`
    :rtype: boolean

    :mod:`os` provides some useful constants for mode:

        * :data:`os.R_OK`
        * :data:`os.W_OK`
        * :data:`os.X_OK`
    """
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode

    def __call__(self):
        return os.access(self.path, self.mode)

    def pp_mode(self):
        """Pretty-prints the instance"""
        mode = []
        if self.mode & os.R_OK:
            mode.append("R_OK")
        if self.mode & os.W_OK:
            mode.append("W_OK")
        if self.mode & os.X_OK:
            mode.append("X_OK")
        unknown = self.mode - (self.mode & (os.R_OK | os.W_OK | os.X_OK))
        if unknown > 0:
            mode.append(unknown)
        return " | ".join(str(item) for item in mode)

    def __str__(self):
        return "os.access('{0}', {1})".format(self.path, self.pp_mode())


class IsFile(object):
    """A predicate version of :func:`os.path.isfile`.

    :param path: The path to test
    :type  path: string
    :return: True if the path is a file
    :rtype:  boolean
    """
    def __init__(self, path):
        self.path = path

    def __call__(self):
        return os.path.isfile(self.path)

    def __str__(self):
        return "path.isfile('{0}')".format(self.path)


class IsDir(object):
    """A predicate version of :func:`os.path.isdir`.

    :param path: The path to test
    :type  path: string
    :return: True if the path is a directory
    :rtype:  boolean
    """
    def __init__(self, path):
        self.path = path

    def __call__(self):
        return os.path.isdir(self.path)

    def __str__(self):
        return "path.isdir('{0}')".format(self.path)


class IsLink(object):
    """A predicate version of :func:`os.path.islink`.

    :param path: The path to test
    :type  path: string
    :return: True if the path is a link
    :rtype:  boolean
    """
    def __init__(self, path):
        self.path = path

    def __call__(self):
        return os.path.islink(self.path)

    def __str__(self):
        return "path.islink('{0}')".format(self.path)


class IsMount(object):
    """A predicate version of :func:`os.path.ismount`.

    :param path: The path to test
    :type  path: string
    :return: True if the path is a mount point
    :rtype:  boolean
    """
    def __init__(self, path):
        self.path = path

    def __call__(self):
        return os.path.ismount(self.path)

    def __str__(self):
        return "path.ismount('{0}')".format(self.path)

class LargerThan(object):
    """A predicate that returns True if the file is larger than the specified
    size.

    :param path: A path to a file
    :type  path: string
    :param size: Default 1; the size to test for, in bytes
    :type  size: int
    :return: True if the file is larger than the specified size in bytes
    :rtype:  boolean
    """
    def __init__(self, path, size=1):
        self.path = path
        self.size = size

    def __call__(self):
        #noinspection PyUnresolvedReferences
        try:
            return os.path.getsize(self.path) > self.size
        except os.error as exception: #pragma: no cover
            message = exception.message
            if message is None or len(exception.message) == 0:
                message = "File does not exist"
            Logger.warn("LargerThan for '{0}': Ignoring os.error: {1}".format(self.path, message))
            return False

    def __str__(self):
        return "path.ismount('{0}')".format(self.path)


class Glob(object):
    """A Container Object wrapper for glob.iglob.

    :param glob: A :mod:`fnmatch` glob, eg "\*.py"
    :type  glob: string
    :return: An iterator over the files discovered by the glob
    :rtype: iterator

    Usage:

        >>> glob = Glob("*.txt")
        >>> for file in glob:
        ...     print file
        >>> for file in glob:
        ...     print file

    Whenever the :func:`__iter__` method is
    called, the object returns a new iterator created by a call to
    :meth:`glob.iglob`. This means that, unlike :meth:`glob.iglob`,
    :class:`Glob` can be iterated over any number of times.
    """
    def __init__(self, glob):
        self.glob = glob

    def __iter__(self):
        from glob import iglob
        return iglob(self.glob)

    def __str__(self):
        return "Glob '{0}'".format(self.glob)


class Newer(object):
    """A Predicate for testing if some files are newer than another.

    Example: This can be used to compile some sources only if they have changed
    since the last compile::

        @do_if(Newer("src/*.py", "build/*.*"))

    :param source_iterator: A set of source files
    :type  source_iterator: container
    :param target_iterator: A set of target files
    :type  target_iterator: container
    :return: True if the newest file in source_iterator is younger than the
             oldest file in target_iterator
    :rtype:  boolean

    Newer computes the result using this pseudo-logic:

        1. Find the *newest* file in source_iter
            * Call file SOURCE
        2. Find the *oldest* file in target_iter
            * Call file TARGET
        3. Test age of SOURCE against age of TARGET
            * If SOURCE is newer (younger) than TARGET, return ``True``
            * Else return ``False``

    .. note:: If the newest source_iter has exactly the same timestamp as the
       oldest file in the target_iter, :class:`Newer` will return False.

    .. note:: The iterator is likely to be called several times in a single
       build which means an iterator is insufficient - it must be a
       Container Object - an object with the __iter__() method:
       http://docs.python.org/library/stdtypes.html#container.__iter__:

           1. The arguments should evaluate only when called, not created,
              otherwise :class:`Newer` will test only those files present when
              the build file was loaded (and files created or modified in the
              build may be missed)
           2. If the argument is an iterator/generator instance, then the second
              call to :class:`Newer` will return the iterator after it has
              performed an iteration, so the iterator will yield no more files.

    Dovetail provides a simple wrapper of :func:`glob.iglob` in the form of
    :class:`Glob`::

        source = Glob(os.path.join("src", "mypackage", "*.py"))
        target = Glob(os.path.join("build", "doc", "mypackage*.rst"))

        @task
        @Newer(source, target)
        def generate_api_doc():
            return call("sphinx-apidoc -f -o src/mypackage build/doc".split(' '))

    In this example, :class:`Newer` runs if any top-level .py file in src/mypackage
    is newer than the corresponding mypackage*.rst file in build/doc.

    Newer works well with Formic (http://www.aviser.asia/formic),
    which allows an easy construction of rich (Apache Ant) globs. In the
    example below:

        * Source file are all Python files in all subdirectories of
          src/mypackage, excluding tests,
        * Target files are the corresponding mypackage*.rst files in
          build/doc

    ::

        import formic
        source = formic.FileSet(directory="src/mypackage",
                                include="*.py",
                                exclude=["**/*test*/**", "test_*"]
                                )
        target = formic.FileSet(directory="build/doc",
                                include="mypackage*.rst")

        @task
        @Newer(source, target)
        def generate_api_doc():
            return call("sphinx-apidoc -f -o src/mypackage build/doc".split(' '))
    """
    def __init__(self, source_iterator, target_iterator):
        self.source_iter = source_iterator
        self.target_iter = target_iterator

    @staticmethod
    def best(file_iterator, newer=True):
        """Returns the timestamp of the newest (or oldest) file in the file
        iterator argument.

        :param file_iterator: An iterator whose items are file paths
        :type  file_iterator: iterator
        :param newer: Defaults True. Determines if the selector is for the
                      newest (newer=True) or oldest (newer=False) file
        :type  newer: boolean
        :return: The timestamp of the newest (or oldest) file in file_iterator
        :rtype:  the :func:`os.path.getmtime` value of the file"""
        warned = False
        best = None
        for file_name in file_iterator:
            #noinspection PyUnresolvedReferences
            try:
                current = os.path.getmtime(file_name)
                if best is None or \
                   (    newer and current > best) or \
                   (not newer and current < best):
                    best = current
            except os.error: #pragma: no cover
                if not warned:
                    Logger.warn("Newer detected file changes during processing. Ignoring.")
                    warned = True
        return best


    def __call__(self):
        source_time = Newer.best(self.source_iter, newer=True)
        target_time = Newer.best(self.target_iter, newer=False)
        Logger.log("Newer: {0} is newer than {1}".format(self.source_iter, self.target_iter))
        return source_time > target_time

    def __str__(self):
        return "'{0}' newer than '{1}'?".format(self.source_iter, self.target_iter)