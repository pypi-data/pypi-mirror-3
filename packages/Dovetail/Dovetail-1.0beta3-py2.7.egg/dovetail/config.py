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

"""Handles the command-line parameter configuration and the
configuration files"""
from dovetail.util.utilities import enum
from dovetail.constants import DESCRIPTION, EPILOG, VERSION
from dovetail.util.exception import  InvalidEnvironment
from dovetail.util.logging import Logger, LEVEL
from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from ConfigParser import SafeConfigParser
from os import path, getcwd, access, R_OK, environ
from platform import node
from getpass import getuser

REPORTS  = enum(SLOW=0, TREE=1, MODULES=2, DEPEND=3)
INI_FILE = ".dovetail"
INI_EXT  = ".ini"

def create_parser():
    """Creates the command line parser.

    :return: An ArgumentParser instance
    :rtype: :class:`argparse.ArgumentParser`"""
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=DESCRIPTION,
                            epilog=EPILOG,
                            add_help=False)

    execution = parser.add_argument_group("Build")
    virtual = parser.add_argument_group("Virtualenv")
    virtual.add_argument('-e', '--virtualenv', action="store",
                         help="Location of a virtualenv environment to use. Will be created if it does not exist.")
    virtual.add_argument('--clear', action="store_true", default=False,
                         help="Recreates (clears) the virtual environment every time, even if it exists")
    execution.add_argument('-f', dest='build_file', action="store", default="build.py",
                           help="Python file containing build plan, default: build.py")
    execution.add_argument('task', action="store", nargs="*",
                           help="One or more Tasks to build. If none, a list of Tasks is presented")

    level   = parser.add_mutually_exclusive_group()
    level.add_argument("-q", dest="loglevel", action="store_const", const="ERROR",
                       help="Dovetail will report only output from Tasks and its own errors")
    level.add_argument("-v", dest="loglevel", action="store_const", const="INFO",
                       help="Report more information about the decisions in the build")
    level.add_argument("-vv", dest="loglevel", action="store_const", const="DEBUG",
                       help="Debug output from Dovetail")
    nesting = parser.add_mutually_exclusive_group()
    nesting.add_argument('-n', '--nested', dest='nested', action='store_true', default=False,
                         help="Presents output in a structured format")
    nesting.add_argument('-nn', '--no-nest', dest='nested', action='store_false',
                         help="Switches off nesting (if set in a configuration file)")

    report = parser.add_argument_group("Reports")
    report.add_argument('-r', dest="reports", action='append', default=None,
                        choices=[name.lower() for name in REPORTS.names()],
                        help="Run additional reports after the build")

    info = parser.add_argument_group("Information")
    info.add_argument('--version', action='version', version='%(prog)s ' + VERSION + " http://www.aviser.asia/dovetail")
    info.add_argument('--usage', action='store_true', default=False,
                      help="Display usage information")
    info.add_argument('-h', '--help', action="store_true", default=False,
                      help="Display this help. If a task is specified, displays help on the task.")
    info.add_argument('--license', action="store_true",
                      help=SUPPRESS)
    info.add_argument('--warranty', action="store_true",
                      help=SUPPRESS)

    return parser

PARSER = create_parser()

def print_help(out_file=None):
    """Utility function to print the help of the Dovetail argparser.

    :param out_file: Default *None* (std_out). An optional file stream to write the help to
    :type  out_file: File Object
    """
    PARSER.print_help(out_file)

def print_usage(out_file=None):
    """Utility function to print the usage instructions of the Dovetail
    argparser.

    :param out_file: Default *None* (std_out). An optional file stream to write the help to
    :type  out_file: File Object
    """
    PARSER.print_usage(out_file)

class Option(object):
    """A class which encapsulates an option in the Dovetail section of the
    configuration file, and the code to validate the entry and map it to
    the internal data model.

    :param name: Name of an Option group
    :type  name: string
    :param validator: Defaults *None*. A function that validates a value in the config file
                      If *None*, no validation is performed
    :type  validator: function(string)
    :param mapper: Defafult *None*. A function that converts a value found in a config file to
                   the appropriate internal type and value. If *None*, the value is isomorphic
                   - it is not mapped.
    :type  mapper: function(string)
    """
    _index = {}
    def __init__(self, name, validator=None, mapper=None):
        self.name      = name
        self.validator = validator if validator else lambda x:x
        self.mapper    = mapper if mapper else lambda x:x
        Option._index[name] = self

    @staticmethod
    def lookup(name):
        """Returns the :class:`Option` with the given name."""
        return Option._index[name]

    def map(self, value):
        """Converts the value into the appropriate representation
        for the option using the :class:`Option` 'mapper' function.

        :param value: A value to look up
        :type  value: string
        :return: The mapped value
        :raises: :exc:`ValueError` if *value* does not validate
        """
        try:
            self.validator(value)
        except ValueError:
            raise
        except Exception as exception:
            raise ValueError("{0} is not a valid value for {1} (Exception: {2})".format(value, self.name, exception))
        return self.mapper(value)

TRUE  = [  'true', 't',  'on', 'yes', 'y', '1', "ok"]
"""Values that are considered 'True' in the configuration file"""
FALSE = [ 'false', 'f', 'off',  'no', 'n', '0']
"""Values that are considered 'True' in the configuration file"""
BOOLEAN = list(TRUE)
"""A conjunction of :data:`TRUE` and :data:`FALSE`"""
BOOLEAN.extend(FALSE)


def split_on_spaces(words):
    """Returns a list of space-separated items in the string; if the string
    is empty, an empty list is returned

    :param words: A space-separated series of items
    :type  words: string
    :return: Splits the string on spaces, returning a list of items. If *words*
             if *None* or empty, the empty list is returned
    :rtype: list
    """
    if words is None or len(words) == 0:
        return []
    return words.split(' ')

def is_a_boolean(boolean_as_string):
    """Returns without error if the string can be mapped to a boolean.

    :param boolean_as_string: The string from a config file
    :type  boolean_as_string: string
    :return: The value as a boolean
    :rtype:  boolean
    :raises: :exc:`ValueError` if *boolean_as_string* is not in :data:`BOOLEAN`
    """
    if not boolean_as_string.lower() in BOOLEAN:
        raise ValueError("Cannot interpret {0} as a boolean. Try True/False, Yes/No, On/Off, 0/1 instead.".format(boolean_as_string))

def coerce_to_boolean(boolean_as_string):
    """Returns the string as a boolean.

    :param boolean_as_string: A string, eg from the config file
    :type  boolean_as_string: string
    :return: The boolean representation of *boolean_as_string*
    :rtype: boolean

    :func:`coerce_to_boolean` is not case sensitive. It looks up appropriate
    values for *True* from :data:`TRUE`.

    It is assumed that *boolean_as_string* is valid (i.e. has already
    been passed to :func:`is_a_boolean` without :exc:`ValueError`
    """
    return boolean_as_string.lower() in TRUE

def map_to_log_level(level):
    """Returns the correct enumeration value for the Log Level.

    :param level: A Log :data:`dovetail.util.logging.LEVEL` value
    :type  level: string
    :return: The log level enumeration value
    :rtype: int
    :raises: :exc:`ValueError` if *level* is not a valid log level"""
    try:
        return LEVEL.lookup(level.upper())
    except KeyError:
        raise ValueError("{0} is not a valid log level. Try DEBUG, INFO, MAJOR, WARN or ERROR.")

# Initialise the Option processors for Dovetail section
Option("virtualenv")
Option("build_file")
Option("clear",    mapper=coerce_to_boolean, validator=is_a_boolean)
Option("nested",   mapper=coerce_to_boolean, validator=is_a_boolean)
Option("task",     mapper=split_on_spaces)
Option("reports",  mapper=split_on_spaces)
Option("loglevel", validator=map_to_log_level)

def load_config_file(config_file):
    """Loads the config file named in config_file into a SafeConfigParser,
    validating the file argument

    :param config_file: A path to a configuration file to be read
    :type  config_file: string
    :return: A configuration parser with the file loaded in it
    :rtype: :class:`ConfigParser.SafeConfigParser`
    """
    if path.isdir(config_file):
        raise InvalidEnvironment("Configuration file {0} is actually a directory".format(config_file))
    if not path.isfile(config_file):
        # The config file doesn't exist, so return silently
        Logger.debug("No configuration file {0}".format(config_file))
        return
    if not access(config_file, R_OK):
        raise InvalidEnvironment("Configuration file {0} is not readable".format(config_file))

    parser = SafeConfigParser()
    parser.optionxform = str
    parser.read(config_file)

    def str_file_name():
        """New __str__ function returning the name of the configuration file"""
        return "Configuration file '{0}'".format(config_file)
    parser.__str__ = str_file_name
    return parser

def apply_config_to_args(parser, args):
    """Takes a config file (in parser) and applies the Dovetail section
    to the argparser (or dictionary) in args.

    :param parser: A ConfigParser with loaded file
    :type  parser: ConfigParser.ConfigParser
    :param args:   The ArgumentParser constructed from the command line
    :type  args:   argparser.ArgumentParser
    :raises: :exc:`dovetail.util.exception.InvalidEnvironment`"""
    if parser.has_section("Dovetail"):
        section = parser.items("Dovetail")
        for name, value in section:
            Logger.debug("{0} Dovetail argument: {1} = {2}".format(str(parser), name, value))
            try:
                option = Option.lookup(name)
            except KeyError:
                raise InvalidEnvironment("{0}, section [Dovetail]: Illegal entry '{1}'".format(str(parser), name))
            try:
                args[name] = option.map(value)
            except Exception:
                raise InvalidEnvironment("{0}, section [Dovetail]: Entry '{1}' has illegal value '{2}'".format(str(parser), name, value))

def apply_config_to_environ(parser):
    """Reads the Environment section of a ConfigParser, writing all entries
    to os.environ.

    :param parser: The ConfigParser
    :type parser: class:`ConfigParser.ConfigParser`

    For each item in [Environment], an environment variable will be set
    in :data:`os.environ` with the item's value."""
    if parser.has_section("Environment"):
        section = parser.items("Environment")
        for name, value in section:
            Logger.debug('{0}: setting ${1}="{2}"'.format(str(parser), name, value))
            environ[name] = value

def find_best_config():
    """Looks at the various ini file locations and probes them; if it finds
    a config file, it will use :func:`load_config_file` to load the file,
    and return the then return the :class:`ConfigParser.SafeConfigParser` for it.

    :return: A ConfigParser loaded from the best configuration file found or *None*
    :rtype:  :class:`ConfigParser.SafeConfigParser`

    See :func:`load_config` for more details
    """
    current = getcwd()
    home    = path.expanduser("~")
    host    = node()
    user    = getuser()
    config_files = [ path.join(current, INI_FILE + "." + user + INI_EXT),
                     path.join(current, INI_FILE + "." + host + INI_EXT),
                     path.join(current, INI_FILE +              INI_EXT),
                     path.join(home,    INI_FILE +              INI_EXT),
                   ]

    for config_file in config_files:
        parser = load_config_file(config_file)
        if parser:
            return parser

def load_config(command_line_args):
    """Loads the configuration for Dovetail from configuration files and
    the command-line arguments; command line overrides configuration files.

    :param command_line_args: The command line arguments
    :type  command_line_args: list of string
    :return: An ArgumentParser with modifications from the config file
    :rtype:  :class:`argparse.ArgumentParser`

    The configuration file is found with :func:`find_best_config`.
    It is in two sections:

    * Section **Dovetail**:
        * Items are defined by the :class:`Option` instances defined in
          this file.
        * :func:`apply_config_to_args` applies the config file to the
          arguments
    * Section **Environment**:
        * For each item in this section, an environment variable will be set
          in :data:`os.environ` with the item's value
        * :func:`apply_config_to_environ` reads and applies the values
    """
    # Find and load the best ini, if any
    parser = find_best_config()
    args = {}
    if parser:
        apply_config_to_args(parser, args)
        apply_config_to_environ(parser)
        tasks = args.get('task')
        # Apply the command line options over it
        namespace = type("Arguments", (), args)
    else:
        namespace = None
        tasks     = None

    args = PARSER.parse_args(command_line_args, namespace=namespace)

    if args.task == [] and tasks is not None and not args.help:
        # If the user did not specify tasks, we _may_ want to default them
        # from the config file, but NOT if the user entered dovetail -h
        args.task = tasks

    args.task = [ task_name for task_name in args.task if task_name != "" ]

    # Set log level as early as possible to ensure reported log lines are what the user
    # actually wanted
    if args.loglevel:
        Logger.set_level(args.loglevel)
    Logger.set_nested(args.nested)

    if parser:
        Logger.log("Loaded config file: {0}".format(parser))
    else:
        Logger.debug("No configuration file found")
    return args
