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
"""A :pep:`302` Python import hook for loading build scripts with
classes that model the loaded packages and modules.

This behaves differently from the built-in loader by loading Python files
from subdirectories **without the presence of the __init__.py**.

The loader is created on a base directory and searches by converting
them into a directory under the base. For example::

    >>> # assuming a file "build.py" in /path/to/build/root
    >>> load("/path/to/build/root/build.py")
    Building in /path/to/build/root
    >>> # assuming build.py in directory ./path/to/directory under /path/to/build/root
    >>> load("path/to/directory/build.py")
    >>> # assuming @task declared on a function test() in build.py above
    >>> build("path.to.directory.build:test")
"""

from os import path, access, R_OK
from sys import modules, meta_path
from imp import new_module, load_source
from inspect import stack
from dovetail.util import InvalidBuildFile, NoSuchModule, NoSuchTask, Logger, tree

WARNING = "{0} is not being imported from under the build root. \
It will not participate in automatic dependency propagation"

class PackageNode:
    """A data structure for describing package structure and which
    packages are associated with :class:`BuildModule` instances.

    :class:`PackageNode` is a model of the tree structure of the build files
    loaded by Dovetail and their relative directory locations. It closely
    resembles the package structure in Python and uses the same
    dotted notation as Python.

    :param full_name: The full name of the package being loaded
    :type  full_name: string

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | name         | string               | The non-qualified name of this file      |
    +--------------+----------------------+------------------------------------------+
    | full_name    | string               | The full Python-style package name for   |
    |              |                      | this package, eg for top/subdir/build.py,|
    |              |                      | full name is top.subdir.build            |
    +--------------+----------------------+------------------------------------------+
    | parent       | :class:`PackageNode` | The parent of this instance              |
    +--------------+----------------------+------------------------------------------+
    | children     | set of :class:`\     | The child packages of this package       |
    |              | PackageNode`         |                                          |
    +--------------+----------------------+------------------------------------------+
    | build_module | :class:`BuildModule` | For a :class:`PackageNode` representing a|
    |              |                      | file (rather than directory) this points |
    |              |                      | to the corresponding                     |
    |              |                      | :class:`BuildModule`, otherwise *None*   |
    +--------------+----------------------+------------------------------------------+
    """

    _index_name = {}   # Index of packages keyed by full name
    _root       = None # root of the Package graph

    @staticmethod
    def get_root():
        """Returns the root :class:`PackageNode` of the package graph"""
        PackageNode._validate()
        return PackageNode._root

    @staticmethod
    def invalidate():
        """Invalidates the package graph forcing re-discovery
        next time get_root is called.

        This is called whenever the :pep:`302` hook 'BuildLoader' detects
        that import has been called"""
        if PackageNode._root is not None:
            PackageNode._root.delete()
            assert not PackageNode._index_name
            PackageNode._root = None

    @staticmethod
    def _validate():
        """Ensure the cache is filled, and if not, discover and build the package graph"""
        if PackageNode._root is None:
            # Create/register logical root
            PackageNode._root = PackageNode("")

            # Get all possible nodes
            nodes = [ PackageNode(name) for name in modules.keys() ]

            # Link them up
            for node in nodes:
                if node.full_name is not None:
                    parent_name = node.full_name.rpartition(".")[0]
                    PackageNode.find(parent_name).add(node)

            # Remove nodes with no relationship to Dovetail
            while True:
                # Repeat stripping of uninteresting leaves until there are no
                # leaves left which are uninteresting
                leaves = [ node for node in PackageNode._index_name.values()
                           if node.is_leaf() and node.build_module is None ]
                if leaves:
                    for leaf in leaves:
                        leaf.delete()
                else:
                    break

    @staticmethod
    def find(module):
        """Finds a :class:`PackageNode` instance for the given package.

        :param module: Name of the package to find
        :type  module: string or :class:`BuildModule`
        :return: The associated :class:`PackageNode`
        :rtype:  :class:`PackageNode`
        :raises: :exc:`KeyError` if there is no such :class:`PackageNode`

        The :class:`PackageNode` graph does not include packages that are loaded
        but are independent of the build files loaded by :func:`.load` (and
        have corresponding :class:`BuildModule` instances)
        """
        assert module is not None
        PackageNode._validate()
        if isinstance(module, basestring):
            task_name = module
        else:
            # Assume module is a instance of module
            task_name = module.__name__
        return PackageNode._index_name[task_name]

    @staticmethod
    def report_modules():
        """Prints a graph of the :class:`PackageNode` instances to the console"""
        def children(node):
            """Helper function to walk the graph of modules; returns children
            of a node with the leaves listed before the nodes"""
            leaves = [ child for child in node.children if child.is_leaf() ]
            nodes  = [ child for child in node.children if not child.is_leaf() ]
            return leaves + nodes
        def display(node):
            """Helper function to produce the text for each node in the
            module report"""
            if node.build_module:
                package_name = node.build_module.name
                return "{0}.py [Name: {1}]".format(node.name, package_name)
            else:
                return node.name
        print "Package structure:"
        root = PackageNode.get_root()
        tree(root, children, node_text=display, display_root=False, indent=3, node_style=True)

    def __init__(self, full_name):
        self.children  = set()
        self.parent       = None

        if full_name is None:
            # This is the logical root
            self.full_name    = None
            self.name         = None
            self.build_module = None
        else:
            if "." in full_name:
                self.name = full_name.rpartition(".")[2]
            else:
                self.name = full_name

            self.full_name = full_name
            PackageNode._index_name[full_name] = self
            try:
                self.build_module = BuildModule.find(full_name)
            except NoSuchModule:
                self.build_module = None

    def is_leaf(self):
        """Returns True if the node is a leaf (eg no :class:`PackageNodes`
        have been loaded by this node"""
        return len(self.children) == 0

    def child(self, name):
        """Find a child of the given name.

        :param name: The name to search for in :attr:`children`
        :type  name: string
        :return: The child :class:`PackageNode` if present, else *None*
        :rtype: :class:`PackageNode`
        """
        match = [ a for a in self.children if a.name == name ]
        if match:
            return match[0]
        else:
            return None

    def add(self, node):
        """Adds a PackageNode as a child of this one.

        :param node: The :class:`PackageNode` to be added to :attr:`children`
        :type  node: :class:`PackageNode`
        """
        assert node is not None
        assert isinstance(node, PackageNode)
        self.children.add(node)
        node.parent = self

    def delete(self):
        """Recursively removes this node and children from the graph"""
        if self.build_module:
            self.build_module.package_node = None
        if self.children:
            clone = list(self.children)
            for child in clone:
                child.delete()
        if self.parent:
            self.parent.children.remove(self)
        self.parent = None
        del PackageNode._index_name[self.full_name]

    def __str__(self):
        return "PackageNode {0}".format(self.full_name)

class BuildModule(object):
    """An object that represents a single build file loaded in Dovetail.

    All build files must be loaded by Dovetail using :func:`load`. Dovetail
    will not run :class:`.Task` in files loaded by, for example, the **import**
    statement. Indeed, if the :class:`.Task` functions are called directly,
    Dovetail will decline to run them.

    :class:`BuildModule` works with :class:`PackageNode`. The latter represent
    each loaded *package*. Leaves on the package tree *may* be modules. These
    modules are modelled by a :class:`BuildModule`.

    :param fullname:  The unqualified name of the module containing the build file
                      (the name of the file, less the .py extension)
    :type  fullname:  string
    :param file_name: The path to the file being loaded
    :type  file_name: string

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | name         | string               | The unqualified name of the module       |
    |              |                      | containing the build file (the name of   |
    |              |                      | the file, less the .py extension)        |
    +--------------+----------------------+------------------------------------------+
    | file_name    | string               | The file name of the loaded build file   |
    +--------------+----------------------+------------------------------------------+
    | module       | :class:`module`      | Reference to the Python module containing|
    |              |                      | the build. Note that                     |
    |              |                      | :attr:`module.__file__` is equal to      |
    |              |                      | :attr:`file_name`                        |
    +--------------+----------------------+------------------------------------------+
    | parent       | :class:`BuildModule` | The BuildModule that loaded (directly or |
    |              |                      | indirectly) this BuildModule             |
    +--------------+----------------------+------------------------------------------+
    | tasks        | dict of {string:     | A dict of task-name -> :class:`.Task`    |
    |              | :class:`.Task`}      | instance. The key is the short name for  |
    |              |                      | the :class:`.Task`                       |
    +--------------+----------------------+------------------------------------------+
    | loaded       | list of              | A list of BuildModule instances which    |
    |              | :class:`BuildModule` | this build file directly (or indirectly) |
    |              |                      | loaded. The order of the list is the     |
    |              |                      | order the dependencies where loaded.     |
    +--------------+----------------------+------------------------------------------+
    """

    root           = None
    """:type: :class:`BuildModule`

    A reference to the build's root build file"""

    base_directory = None
    """:type: string

    The base directory for the build"""

    _all           = {}   # All BuildModules indexed by module name
    _current       = None # Used to track hierarchy while importing build files

    def __init__(self, fullname, file_name, module=None):
        """Instantiates a BuildModule - normally done by the import hook."""
        self.name         = fullname
        self.module       = module
        self.tasks        = {}
        self.parent       = BuildModule._current
        self.loaded       = []
        self.file_name    = file_name

        BuildModule._all[fullname] = self
        BuildModule._current = self

        if BuildModule.root is None:
            BuildModule.root = self
        if self.parent is not None:
            self.parent.loaded.append(self)

    def _finish_loading(self, module):
        """Internal method called at the end of importing a Python files.

        This allows a hierarchy of BuildModule objects to be created"""
        self.module   = module
        BuildModule._current = self.parent

    @staticmethod
    def current():
        """Get the build module that's currently running.

        :return: the highest :class:`BuildModule` found in the stack.
        :rtype:  :class:`BuildModule`
        """
        for frame in stack():
            module_name = frame[0].f_globals["__name__"]
            try:
                return BuildModule.find(module_name)
            except NoSuchModule:
                pass
        Logger.warn("Failed to find any Dovetail module on the call stack. Did you use dovetail.load()?")
        return None

    @staticmethod
    def find(module):
        """Finds the :class:`BuildModule` for the Python :class:`module` argument

        :param module: The module to search for
        :type  module: Python :class:`module` instance *or* the name of the module
        :return: The :class:`BuildModule` that wraps the :class:`module`
        :rtype: :class:`BuildModule`
        :raises: :exc:`.NoSuchModule` if the module was not loaded by Dovetail"""
        if isinstance(module, basestring):
            module_name = module
        else:
            module_name = module.__name__

        try:
            return BuildModule._all[module_name]
        except KeyError:
            raise NoSuchModule("Module {0} is not a recognized build module - it should be underneath the build root".format(module))

    @staticmethod
    def register_task(task):
        """Register a task with the :class:`BuildModule` database.

        :param task: The task that has just been loaded
        :type  task: :class:`.Task`
        :raises: :exc:`.NoSuchModule` if the task was declared in a file that
                 was not loaded *via* :func:`load`"""
        assert task is not None
        try:
            module = BuildModule.find(task.module)
            module.tasks[task.func_name] = task
        except NoSuchModule:
            Logger.warn(WARNING.format(task))
            raise

    def find_task(self, name):
        """Searches for task name in this BuildModule and it's children.

        :param name: The name of a :class:`.Task`. Accepts both non-qualified
                     and fully-qualified :class:`.Task` names
        :type  name: string
        :return: The task
        :rtype:  :class:`.Task`
        :raises: :exc:`.NoSuchTask`
        """

        def _find_package(current_package, package_name):
            """Helper function to walk the package tree to find the
            package specified by package_name"""
            assert current_package is not None
            assert package_name is not None
            for sub in package_name.split("."):
                child = current_package.child(sub)
                if child is None:
                    valid = [ package.name for package in current_package.children ]
                    if valid:
                        msg = "Valid packages: " + ", ".join(valid)
                    else:
                        msg = "No further packages"
                    if current_package.full_name == "":
                        package_msg = ""
                    else:
                        package_msg = " under '{0}'".format(current_package.full_name)
                    raise NoSuchTask("There is no package '{0}'{1}. {2}".
                                        format(sub, package_msg, msg))
                current_package = child

            return current_package

        def _find_task_in_package(package, task_name):
            """Helper function to find a task given a starting package;
            name is a string of the form package.subpackage.file:task"""
            assert package is not None
            assert task_name is not None
            if package.build_module is None:
                raise NoSuchTask("Task '{0}' does not exist in '{1}' - this package was not loaded by dovetail.load()".
                format(name, package.full_name))
            try:
                return package.build_module.tasks[task_name]
            except KeyError:
                all_tasks = [ task.func_name for task in package.build_module.tasks.values() ]
                if all_tasks:
                    if len(all_tasks) > 5:
                        all_tasks = all_tasks[0:4]
                        all_tasks.append("...")
                        msg = "Tasks include " + ", ".join(all_tasks)
                    else:
                        msg = "Tasks: " + ", ".join(all_tasks)
                else:
                    msg = "There are no tasks in this module"
                raise NoSuchTask("Task '{0}' does not exist in module '{1}'. {2}".
                format(task_name, package.full_name, msg))

        package = PackageNode.find(self.module)

        if ":" in name:
            # If using dotted form, need to go up to the parent package
            # to search the peers of this module
            package_name, _, task_name = name.partition(":")
            try:
                package = _find_package(package.parent, package_name)
            except NoSuchTask as exception:
                raise NoSuchTask("Error in task name {0}: {1}".format(name, str(exception)))
        else:
            task_name = name

        return _find_task_in_package(package, task_name)

    def get_relative_file_name(self):
        """Returns the file name, relative to the build root, of this module"""
        root = path.dirname(BuildModule.root.file_name)
        return path.relpath(self.file_name, root)

    def get_child_tasks_with_name(self, name):
        """Interrogates children directly loaded by this module and returns
        a list of Tasks with the name given in the argument.

        This method allows a Task, say 'clean', in a parent build file
        to automatically call 'clean' in each of its descendants.

        :param name: The name of a :class:`.Task`. The name must be the function
                     name, not the fully qualified name.
        :type  name: string
        :return: All the tasks with that name under this :class:`BuildModule`
        :rtype: list of :class:`.Task` (may be an empty list)
        """
        child_tasks = []
        for child in self.loaded:
            task = child.tasks.get(name)
            if task is None:
                skipped_generation = child.get_child_tasks_with_name(name)
                child_tasks.extend(skipped_generation)
            else:
                child_tasks.append(task)
        return child_tasks

    @staticmethod
    def report_load_graph():
        """Print a tree of all build files (modules) loaded by calls to :func:`load`"""
        def loaded(module):
            """Helper function to return the children of a given node
            to enable the report to walk the tree"""
            return module.loaded
        def display(module):
            """Helper function to return the text to display for each node
            of the load report"""
            rel_dir = module.get_relative_file_name()
            return rel_dir
        print "Load Graph:"
        print "Base directory:", path.dirname(BuildModule.root.file_name)
        tree(BuildModule.root, loaded, node_text=display, indent=5, node_style=True)

    def __str__(self):
        if self.module is None:
            return "BuildModule {0} - still loading".format(self.name)
        else:
            return "BuildModule {0} [File={1}]".format(self.name, self.module.__file__)

class BuildLoader(object):
    """A :pep:`302` Python loader to import build scripts and their dependencies."""
    def __init__(self, base_directory):
        if not path.isdir(base_directory):
            raise InvalidBuildFile("{0} is not a directory".format(base_directory))
        if not access(base_directory, R_OK):
            raise InvalidBuildFile("Directory {0} does not exist or is not readable".format(base_directory))

        self.base_directory = base_directory
        Logger.major("Working directory: {0}".format(self.base_directory))

    @staticmethod
    def loaded():
        """Returns true if a :class:`BuildLoader` import hook as been installed"""
        return any(item for item in meta_path if isinstance(item, BuildLoader))

    @staticmethod
    def register(base_directory):
        """Creates and registers a BuildLoader instance with the Python
        loader.

        :param base_directory: The base directory for the build. Files outside
                               this directory will not load
        :type  base_directory: string
        :return: The build loaded singleton
        :rtype: :class:`BuildLoader`

        .. warning::

            This must be called precisely once"""
        assert not BuildLoader.loaded()
        loader = BuildLoader(base_directory)
        Logger.debug("Installing PEP 302 Import hook: {0}".format(loader))
        meta_path.append(loader)
        return loader


    #noinspection PyUnusedLocal
    # pylint: disable-msg=W0613
    def find_module(self, fullname, locations=None):
        """A :pep:`302` import hook for :class:`BuildLoader`"""
        # Since files are being loaded, clear PackageNode cache
        PackageNode.invalidate()

        components = fullname.split(".")
        location = path.join(self.base_directory, *components)

        if path.isfile(path.join(location, "__init__.py")):
            return None

        file_name = location + ".py"
        if path.isfile(file_name) and access(file_name, R_OK):
            return BuildLoader.FileLoader(self, file_name)
        elif path.isdir(location) and access(location, R_OK):
            return BuildLoader.DirectoryLoader(self, location)
        else:
            return None

    def __str__(self):
        return "BuildLoader on '{0}'".format(self.base_directory)

    class DirectoryLoader(object):
        """A class implementing a :pep:`302` load_module import hook for a directory.

        Directories loaded into Dovetail with this loader contain ONLY references
        to the packages loaded from their directory. Otherwise they are empty and
        do not have the __init__.py semantics"""
        def __init__(self, loader, location):
            self.loader = loader
            self.location = location

        def load_module(self, fullname):
            """:pep:`302` load_module implementation"""
            Logger.debug("DirectoryLoader.load_module('{0}')".format(fullname))
            if fullname in modules:
                mod = modules[fullname]
            else:
                mod = modules.setdefault(fullname, new_module(fullname))

            mod.__file__    = self.location
            mod.__name__    = fullname
            mod.__path__    = [ self.location ]
            mod.__package__ = fullname
            Logger.debug(" -> Returning empty module for {0}: {1}".format(fullname, mod))
            return mod

    class FileLoader(object):
        """A class implementing a :pep:`302` load_module import hook for a file.

        Files can be loaded from any subdirectory of base_directory. Functions
        and classes can be referenced like::

            >>> import path.to.file
            >>> path.to.file.function()

        Or::

            >>> from path.to.file import function
            >>> function()
        """
        def __init__(self, loader, file_name):
            self.loader = loader
            self.file = file_name

        def load_module(self, fullname):
            """:pep:`302` load_module implementation"""
            Logger.debug("FileLoader.load_module('{0}') on {1}".format(fullname, self.file))

            if fullname in modules:
                mod = modules[fullname]
            else:
                loader = BuildModule(fullname, self.file)
                mod = load_source(fullname, self.file)
                mod.__file__    = self.file
                mod.__name__    = fullname
                mod.__path__    = [ path.dirname(self.file) ]
                mod.__package__ = None
                loader._finish_loading(mod)
                modules.setdefault(fullname, mod)

            Logger.debug(" -> Returning module for {0}: {1}".format(fullname, mod))
            return mod

def is_loaded():
    """Returns whether Dovetail has loaded itself and is ready to load directives"""
    return BuildLoader.loaded()

def load_from_import():
    import os
    import sys

    Logger.debug("Call to load_from_import - checking if this is a third-party import")

    # Determine installation directory
    installed_at = os.path.dirname(__file__)
    pure_dovetail = True
    Logger.debug("Searching stack frame for caller:")
    for frame in stack():
        file_path = frame[1]
        func_name = frame[3]
        module_name = frame[0].f_globals["__name__"]

        Logger.debug("   Module File: {0} Module: {1} Func: {2}".format(file_path, module_name, func_name))
        if not file_path.startswith(installed_at):
            if module_name == "pkg_resources" and func_name == "load":
                Logger.debug("      Detected an invocation through pkg_resources")
                break

            if module_name == "__main__" and \
               func_name == "<module>" and \
               file_path.endswith("bootstrap.py"):
                Logger.debug("      Detected an invocation through virtual machine bootstrap")
                break

            if module_name == "__main__" and\
               func_name == "<module>":
                Logger.debug("Loading module is not the Dovetail script")
                pure_dovetail = False
                break

    if pure_dovetail:
        Logger.debug("Dovetail imported via command line: No need to initialize yet")
        return

    module = sys.modules[module_name]
    file_path = os.path.abspath(module.__file__)

    # Test to see if there is an __init__.py in the same directory as
    # the targeted module
    dir_name = os.path.dirname(file_path)
    init = os.path.join(dir_name, "__init__.py")
    if os.path.isfile(init):
        raise InvalidBuildFile("dovetail.load('{0}') failed:\n"
                               "    There is an __init__.py in the same directory as {0}\n"
                               "    Dovetail build files cannot be located in Python packages.".format(file_path))

    # Register the loader
    BuildModule.base_directory = dir_name
    BuildLoader.register(BuildModule.base_directory)
    BuildModule(module.__name__, file_path, module)

def load(file_path):
    """Load a build file which may be specified as a relative or absolute
    path (relative paths are relative to the file of the calling script).

    Load will only load files in or under the build root (which is set
    as the directory containing the first build file loaded by Dovetail).

    Paths may be specified with either forward or backward slash.

    >>> # Load another.py in the same directory as the calling script
    >>> load("another.py")

    >>> # Load another.py in directory 'dir' under the directory of the calling
    >>> # script:
    >>> load("dir/another.py")
    >>> # or
    >>> load("dir\\another.py")

    >>> # Load a specific file:
    >>> load("/path/to/build/root/build.py")

    The very first call to :func:`load` should either supply an absolute path
    which will set the build's base directory. Failing this, the current
    working directory is used to establish the build root.
    """
    assert file_path is not None, "load() was called with the file_path argument set to None"

    if not file_path.endswith(".py"):
        raise InvalidBuildFile("Build file {0} must be a Python source file ('.py' extension)".format(file_path))

    def normalize_path(module):
        """Change the separator in the module argument to the platform
        appropriate path separator (to handle windows/unix issues)"""
        not_path_sep = "\\" if path.sep == "/" else "/"
        return module.replace(not_path_sep, path.sep)

    def find_module():
        """Find and return the build module closest to the top of the stack"""
        frames = stack()
        frames.reverse()
        last = None
        while frames:
            frame = frames.pop()
            module_name = frame[0].f_globals["__name__"]
            if module_name != last:
                last = module_name
                #assert "__main__" != module_name, \
                #        "Failed to find any loaded module on the stack"
                try:
                    return BuildModule.find(module_name)
                except NoSuchModule:
                    pass

    request = path.normpath(normalize_path(file_path))

    if path.sep in request:
        # Test to see if there is an __init__.py in the same directory as
        # the targeted module
        dir_name = path.dirname(request)
        init = path.join(dir_name, "__init__.py")
        if path.isfile(init):
            import traceback
            for line in traceback.extract_stack():
                print line
            raise InvalidBuildFile("dovetail.load('{0}') failed:\n"
                    "    There is an __init__.py in the same directory as {0}\n"
                    "    Dovetail build files cannot be located in Python packages.".format(file_path))

    relative     = False
    build_module = None
    if BuildLoader.loaded():
        if not path.isabs(request):
            # If location of caller is not specified, use their BuildModule's location
            relative = True
            build_module = find_module()
            build_dir    = path.dirname(build_module.file_name)
            request = path.join(build_dir, request)
        request = path.normpath(request)
    else:
        # No file has been loaded, path must be made absolute.
        request = path.abspath(request)

    Logger.debug("Request load of {0} resolved to {1}".format(file_path, request))
    if not access(request, R_OK):
        if relative:
            raise InvalidBuildFile("File {0} under {1} does not exist or is not readable".format(file_path, build_module.file_name))
        else:
            raise InvalidBuildFile("File {0} does not exist or is not readable".format(file_path))

    if BuildLoader.loaded():
        # Get build root
        root = path.dirname(BuildModule.root.file_name)

        # Validate that this is under build root
        rel = path.relpath(request, root)
        if rel.startswith(".."):
            if relative:
                raise InvalidBuildFile("{0} called from {1} is not in or underneath the build root: {2}".
                            format(file_path, build_module.file_name, root))
            else:
                raise InvalidBuildFile("{0} is not in or underneath the build root: {1}".
                            format(file_path, root))
    else:
        # Register the loader
        BuildModule.base_directory = path.dirname(request)
        BuildLoader.register(BuildModule.base_directory)
        rel = path.basename(request)

    # Work out the 'official' package name
    package_name, _, _ = rel.replace(path.sep, ".").rpartition(".")

    # call __import__
    __import__(package_name, level=0)
    return modules[package_name]