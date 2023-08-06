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

"""Utility functions."""

import subprocess

VIRTUALENV = None
def get_virtual_environment():
    """Gets the path of this virtual environment, if dovetail is running as
    a slave, otherwise None"""
    return VIRTUALENV

def set_virtual_environment(virtualenv):
    """Sets the path to the slave virtualenv environment.

    See get_virtual_environment()"""
    global VIRTUALENV
    VIRTUALENV = virtualenv

def args_as_str(*kw, **kwargs):
    """Pretty prints a list of arguments of a function"""
    list_args = list(kw)
    list_args.extend([ "{0}={1}".format(name, value) for name, value in kwargs.iteritems()])
    if list_args is None:
        return ""
    else:
        return ", ".join(str(item) for item in list_args)

def enum(**enums):
    """Creates an instance of an Enum class, instantiated with values.

    Usage::

        >>> Numbers = enum(ONE=1, TWO=2, THREE='three')
        >>> Numbers.ONE
        1
        >>> Numbers.TWO
        2
        >>> Numbers.THREE
        'three'

    Enums are created with the following methods:

        * ``as_str()``. Returns the string name of the instance::

              >>> Numbers.as_str(Numbers.ONE)
              'ONE'

        * ``contains(value)``: Returns True if the value is a member of the
          enumeration::

              >>> Numbers.contains(Numbers.ONE)
              True
              >>> Numbers.contains('ONE')
              False
              >>> Numbers.contains(1)
              True

        * ``lookup(name)``: Looks up an instance by the name of the key::

              >>> Numbers.lookup('ONE')
              1

          ``lookup(name)`` and ``as_str()`` are reflexive. For any member **m** of an
          enumeration **e**, the following *must* be true::

              >>> e.lookup(e.as_str(e.m)) is e.m
              True

        * ``names()``: Returns a list of names in the enumeration::

              >>>Numbers.names()
              ['THREE', 'TWO', 'ONE']
    """
    enumeration = enums.copy()
    def as_str(item):
        """Returns the name of the enum instance"""
        for key, value in enums.iteritems():
            if value == item:
                return key
        raise KeyError('Enum does not contain value {0}'.format(item))

    def contains(value):
        """Returns True if the item is a member of the enumeration"""
        return value in set(enums.values())

    def lookup(name):
        """When passed the _name_ of an enumeration, returns its value."""
        return enums[name]

    def names():
        """Returns a list of the names in the enum"""
        return enums.keys()

    enumeration['contains'] = staticmethod(contains)
    enumeration['lookup']   = staticmethod(lookup)
    enumeration['as_str']   = staticmethod(as_str)
    enumeration['names']    = staticmethod(names)
    return type('Enum', (), enumeration)

def stamp_environment():
    """Writes a lot of system information into the os.environ.

    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |Environment Variable Name          | How obtained (eg Python API)           | Eg Win   | Eg Mac                     |
    +===================================+========================================+==========+============================+
    |**About the machine hardware**                                                                                      |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_MACHINE``               | ``platform.machine()``                 | x86      | x86_64                     |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PROCESSOR``             | ``platform.processor()``               | ...      | i386                       |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |**About the OS**                                                                                                    |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_OS_NAME``               | ``os.name``                            | nt       |  posix                     |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_SYSTEM``                | ``platform.system()``                  | Windows  | Darwin                     |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_RELEASE``               | ``platform.release()``                 | XP       | 11.3.0                     |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |**Information about Python itself**                                                                                 |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PYTHON_EXECUTABLE``     | ``sys.executable``                     | *Path to Python executable*           |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PYTHON_IMPLEMENTATION`` | ``platform.python_implementation()``   | CPython, IronPython, PyPy, Jython     |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PYTHON_MAJOR_VERSION``  | ``platform.python_version_tuple()``    | 2        | 2                          |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PYTHON_MINOR_VERSION``  | ``platform.python_version_tuple()``    | 2.7      | 2.7                        |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_PYTHON_VERSION``        | ``platform.python_version_tuple()``    | 2.7.1    | 2.7.1                      |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_BUILD_PLATFORM``        | ``pkg_resourses.get_build_platform()`` | win32    |  macosx-10.7-intel         |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |**About the environment**                                                                                           |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_VERSION``               | :data:`dovetail.constants.VERSION`     | 1.0      | 1.0                        |
    +-----------------------------------+----------------------------------------+----------+----------------------------+
    |``DOVETAIL_NODE``                  | ``platform.node()``                    | *Machine's network name*              |
    +-----------------------------------+----------------------------------------+---------------------------------------+
    |``DOVETAIL_USER``                  | ``getpass.getuser()``                  | *Username of build user*              |
    +-----------------------------------+----------------------------------------+---------------------------------------+
    |``DOVETAIL_VIRTUALENV_SLAVE``      | *Set if running in a slave*            | *Path to virtualenv*                  |
    +-----------------------------------+----------------------------------------+---------------------------------------+
    """
    import os
    from pkg_resources import get_build_platform
    import platform
    from dovetail.constants import VERSION
    from getpass import getuser
    from sys import executable

    # About the machine hardware
    os.environ['DOVETAIL_MACHINE']   = platform.machine()   # eg x86     x86_64
    os.environ['DOVETAIL_PROCESSOR'] = platform.processor() # eg ...     i386

    # About the OS
    os.environ['DOVETAIL_OS_NAME']   = os.name              # eg nt,      posix
    os.environ['DOVETAIL_SYSTEM']    = platform.system()    # eg Windows  Darwin
    os.environ['DOVETAIL_RELEASE']   = platform.release()   # eg XP       11.3.0

    # Information about Python itself
    major, minor, patchlevel = platform.python_version_tuple()
    os.environ['DOVETAIL_PYTHON_EXECUTABLE']     = executable
    os.environ['DOVETAIL_PYTHON_IMPLEMENTATION'] = platform.python_implementation()
    os.environ['DOVETAIL_PYTHON_MAJOR_VERSION']  = "{0}".format(major)
    # eg 2
    os.environ['DOVETAIL_PYTHON_MINOR_VERSION']  = "{0}.{1}".format(major, minor)
    # eg 2.7
    os.environ['DOVETAIL_PYTHON_VERSION']        = "{0}.{1}.{2}".format(major, minor, patchlevel)
    # eg 2.7.1
    os.environ['DOVETAIL_BUILD_PLATFORM']        = get_build_platform()
    # eg win32    macosx-10.7-intel

    # About the environment
    os.environ['DOVETAIL_VERSION'] = VERSION
    os.environ['DOVETAIL_NODE']    = platform.node()        # Machine's hostname
    os.environ['DOVETAIL_USER']    = getuser()              # User's ID
    if get_virtual_environment():
        # Set if running in a virtualenv slave
        os.environ['DOVETAIL_VIRTUALENV_SLAVE'] = get_virtual_environment()

def tree(root, get_children, node_text=str, display_root=True,
                indent=1, separator=1, node_style=False, margin="  "):
    """Produce a hierarchical text tree.

    The function takes three arguments that must 'agree':

        * **root**: A root of a tree. Root and all its descendants must be of duck type <node>.
        * **node_text()**: A function that 'renders' objects of type <node>
        * **get_children()** A function that returns the children of any node. The children
          must be returned in an iterable, such as a list.

    :param root:         The root node of the tree
    :type  root:         Object
    :param node_text:    Function to get display text for
                         a node in the tree. Can return multiple lines.
    :type  node_text:    function(node) -> string
    :param get_children: A function which returns an iterable of the children
                         of a node. These children
                         will be looped over as the next level of nodes.
    :type  get_children: function(node) -> iterable<node>
    :param display_root: If True, the root's text is displayed
                         otherwise only the children are displayed
    :type  display_root: boolean
    :param indent:       Number of characters than each extra level indents
                         by. Defaults to 1 for a horizontally-tight tree
    :type  indent:       int
    :param node_style:   When True, the nodes are different from leaves, and
                         the vertical node expansions are drawn under the node (influenced
                         by the indent argument). When False, the nodes and leaves
                         are drawn the same, vertical expansions are drawn from the main
                         tree
    :type  node_style:   boolean
    :param separator:    Number of lines between each node in the tree. Defaults
                         to 1 to provide some spacing between nodes. Use 0 for a
                         vertically-tighter tree
    :type  separator:    int
    :param margin:       The left margin of the report which is repeated each
                         on each line. Defaults to a two spaces.
    :type  margin:       string
    :return:             A text representation of the tree **root**
    :rtype:              string
    """
    def _tree(node, indent_str, display_node, last):
        """Internal method implementing :func:`tree` with a recursive
        approach"""
        # This test suppresses the purely logical "run" task
        children = get_children(node)
        if display_node:
            if node_style:
                lead = "+- "
            else:
                lead   = "+" + "-"*indent + ("." if children else "-" ) + " "
            extend = (" " if last else "|") + " "*indent + ("|" if children else " ")

            first = True
            lines =  str(node_text(node)).splitlines()
            if lines:
                for line in lines:
                    if first:
                        print "{0}{1}{2}".format(indent_str, lead, line)
                        first = False
                    else:
                        print "{0}{1} {2}".format(indent_str, extend, line)
            else:
                print "{0}{1}".format(indent_str, lead)

            for _ in range(separator):
                print "{0}{1}".format(indent_str, extend)
            indent_str += " "*(indent+1) if last else "|" + " "*indent
        if children:
            last_child = children[-1]
            for child in children:
                _tree(child, indent_str, True, child is last_child)

    _tree(root, margin, display_root, True)

def call(arguments, shell=False,
         stdout=None, stdout_mode="w", stdout_buffer=-1,
         stderr=None, stderr_mode="w", stderr_buffer=-1
         ):
    """A convenience function that wraps subprocess.call() but allows the
    developer to specify stdout and stderr not as streams but files.

    A typical use would be::

        >>> call('pylint src'.split(' '), stdout='pylint.out')

    This would run pylint on the src subdirectory, capturing all stdout in
    the file pylint.out. The opening and closing are automatically
    handled.

    The file's mode and buffer are optionally specified using
    the std[out|err]_mode and std[out|err]_buffer arguments. The values
    and semantics are exactly as in the open(file, mode, buffering)
    function. The defaults are mode="w" and buffering=None.

    The return value is the value returned by the wrapped subprocess.call()
    function.
    """
    out = None
    err = None
    if stdout is not None:
        out = open(stdout, stdout_mode, stdout_buffer)
    try:
        if stderr is not None:
            err = open(stderr, stderr_mode, stderr_buffer)
        try:
            return subprocess.call(arguments, shell=shell, stdout=out, stderr=err)
        finally:
            if err is not None:
                err.close()
    finally:
        if out is not None:
            out.close()
