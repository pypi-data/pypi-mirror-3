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

"""Logging and stdout formatting"""
import sys
from dovetail.util.utilities import enum
from datetime import datetime

# pylint: disable-msg=W0212
# Classes in this module are specifically 'friends' and may access internal
# members for efficiency

LEVEL        = enum(DEBUG=0, INFO=1, MAJOR=2, WARN=3, ERROR=4)
"""Enumeration of different logging levels:

0. DEBUG
1. INFO
2. MAJOR
3. WARN
4. ERROR
"""

LEVEL_PREFIX =      [' ',      '.',    '>',   '!',     '#']

class Message(object):
    """A log message capturing a piece of information about the execution of Dovetail.

    Attributes:

    +--------------+----------------------+------------------------------------------+
    | Attribute    | Type                 | Description                              |
    +==============+======================+==========================================+
    | message      | string               | The line captured from the logging       |
    |              |                      | system                                   |
    +--------------+----------------------+------------------------------------------+
    | level        | Enum from            | The log level                            |
    |              | :data:`LEVEL`        |                                          |
    +--------------+----------------------+------------------------------------------+
    | when         | :class:`datetime.\   | When the message was received            |
    |              | datetime`            |                                          |
    +--------------+----------------------+------------------------------------------+

    .. note::

        The overall reporting level is changed by calling Logging.setLevel()."""
    def __init__(self, message, level=LEVEL.INFO):
        assert LEVEL.DEBUG <= level <= LEVEL.ERROR
        assert message is not None
        assert isinstance(message, basestring)
        self.message = message
        self.level   = level
        self.when    = datetime.now()

    def shown(self):
        """Returns True if this message should be shown (its level >= logging level)"""
        return Logger.show(self.level)

    def __str__(self):
        return "{0} {1}".format(self.when.isoformat(), self.message)


class StdErr(object):
    """A log message which was captured from stderr"""
    def __init__(self, message):
        self.message = str(message).rstrip()

    def shown(self):
        """Returns True if the error should be shown, which is likely
        always True"""
        return Logger.show(LEVEL.ERROR)

    def __str__(self):
        return self.message

class Logger(object):
    """Co-ordinates output from the execution of Dovetail.

    The global variable LEVEL contains an enumeration of the following log levels:

        * LEVEL.DEBUG - Debugging information. Very verbose
        * LEVEL.INTO  - Default level
        * LEVEL.MAJOR - important messages and sys.stdout
        * LEVEL.WARN
        * LEVEL.ERROR - errors and sys.stderr

    The overall reporting level is changed by calling Message.setLevel()"""
    _level    = LEVEL.MAJOR
    _out_raw  = sys.stdout
    _out_nl   = True   # Keep track of terminating newlines
    _err_raw  = sys.stderr
    _err_nl   = True   # Keep track of terminating newlines
    _captured = False
    _frame    = None
    _indent   = ""
    _nested   = False

    @staticmethod
    def set_nested(nested):
        """Switch nesting of the log file on or off.

        Can only be called when Tasks are not executing"""
        if nested == Logger._nested:
            return

        assert Logger._captured
        assert Logger._frame is None
        Logger._nested = nested

    @staticmethod
    def set_level(level):
        """Sets the overall level of log output.

        This setting does not adjust what is *captured*, only what is reported"""
        if isinstance(level, basestring):
            level = LEVEL.lookup(level.upper())

        Logger._level = level
        Logger.log("Setting log level to {0}".format(LEVEL.as_str(level)), level=LEVEL.INFO)

    @staticmethod
    def show(level):
        """Returns True if level >= logging level"""
        return level >= Logger._level

    @staticmethod
    def set_frame(frame):
        """Sets the Logger frame which is used to calculate the indent
        when nesting the logging output"""
        if Logger._nested:
            if frame is None:
                Logger.indent = ""
            else:
                Logger._indent = "  " * frame.depth()
        Logger._frame = frame

    @staticmethod
    def _write_raw(out, indent, level, message):
        """Internal method to write output to stdout or stderr"""
        for line in message.splitlines(True):
            if indent and Logger._nested:
                assert (out is Logger._out_raw and level < LEVEL.ERROR) or \
                       (out is Logger._err_raw and level == LEVEL.ERROR)
                out.write(LEVEL_PREFIX[level])
                out.write('|')
                out.write(Logger._indent)
            out.write(line)

    @staticmethod
    def ends_with_newline(message):
        """Return True if the message ends with a new line"""
        if not len(message):
            return False
        return message[-1] == "\n"

    @staticmethod
    def _write_stdout(level, message):
        """Internal method to write to stdout handling newlines"""
        assert level < LEVEL.ERROR
        Logger._write_raw(Logger._out_raw, Logger._out_nl, level, message)
        Logger._out_nl = Logger.ends_with_newline(message)

    @staticmethod
    def _write_stderr(message):
        """Internal method to write to stderr handling newlines"""
        Logger._write_raw(Logger._err_raw, Logger._err_nl, LEVEL.ERROR, message)
        Logger._err_nl = Logger.ends_with_newline(message)

    @staticmethod
    def flush():
        """Flushes all output to the logging channels"""
        if Logger._captured:
            sys.stderr.flush()

    @staticmethod
    def log(message, level=LEVEL.INFO):
        """Logs a message to the currently executing frame"""
        if Logger._frame:
            Logger._frame.log(Message(message, level))

        if LEVEL.ERROR > level >=  Logger._level:
            Logger._write_stdout(level, message + "\n")
        elif level >= LEVEL.ERROR:
            Logger._write_stderr(message + "\n")

    @staticmethod
    def debug(message):
        """Logs a method at DEBUG level"""
        Logger.log(message, level=LEVEL.DEBUG)


    @staticmethod
    def major(message):
        """Logs a method at MAJOR level"""
        Logger.log(message, level=LEVEL.MAJOR)


    @staticmethod
    def warn(message):
        """Logs a method at ERROR level"""
        Logger.log(message, level=LEVEL.WARN)

    @staticmethod
    def error(message):
        """Logs a method at ERROR level"""
        Logger.log(message, level=LEVEL.ERROR)

    # pylint: disable-msg=R0201
    # TeeOut is a duck-type which requires a write(data) method
    @staticmethod
    def _capture_std_out_and_err():
        """This method replaces the sys.stdout and sys.stderr with variants that
        pipe the data to the Logger"""
        class TeeOut(object):
            """An object that assists the capture of stdout"""
            def __del__(self):
                if Logger: # When called, Logger can have already been destroyed
                    sys.stdout = Logger._out_raw

            def write(self, data):
                """Writes the stdout data to the Logger at MAJOR level"""
                Logger._write_stdout(LEVEL.MAJOR, data)

            def flush(self):
                """Flushes output to the screen, and ensures all logging has
                been flushed from the internal Logger buffers"""
                Logger._out_raw.flush()

        class TeeErr(object):
            """An object that assists the capture of stdout"""
            def __init__(self):
                self.buffer = ""

            def __del__(self):
                if Logger: # When called, Logger can have already been destroyed
                    sys.stderr = Logger._err_raw

            def write(self, data):
                """Writes the stderr data to the Logger at ERROR level"""
                Logger._write_stderr(data)
                if len(data) > 0:
                    self.buffer += data
                    if self.buffer[-1] == '\n':
                        self.flush()

            def flush(self):
                """Flushes output to the screen, and ensures all logging has
                been flushed from the internal Logger buffers"""
                if len(self.buffer) > 0:
                    if Logger._frame is not None:
                        Logger._frame.log(StdErr(buffer))
                    self.buffer = ""
                Logger._err_raw.flush()

        # Start intercepting stdout and stderr
        Logger._captured = True
        sys.stdout = TeeOut()
        sys.stderr = TeeErr()

Logger._capture_std_out_and_err()