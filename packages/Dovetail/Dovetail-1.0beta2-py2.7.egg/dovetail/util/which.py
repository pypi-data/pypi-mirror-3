###############################################################################
# Taken, with permission and amendments, from:
#                 http://stackoverflow.com/a/377028
#
# Copyright (c) 2012, Jay Loden
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Jay Loden nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

"""A multi-platform implementation of the Unix 'which' command in Python."""

from os import environ, path, access, pathsep

def which(program):
    """A Python implementation of the Unix 'which' command, which tests whether
    the argument is a program either directly accessible or is on the system path.

    :param program: The name of a file that should be on the path
    :type program: string
    :return: The full path of the first executable found, or None\
    if the executable is not on the path
    :rtype: string
    """
    def is_exe(filepath):
        """Returns *True* if filepath is an executable"""
        from os import X_OK
        return path.isfile(filepath) and access(filepath, X_OK)

    entry, _ = path.split(program)
    if entry:
        if is_exe(program):
            return program
    else:
        for entry in environ["PATH"].split(pathsep):
            exe_file = path.join(entry, program)
            if is_exe(exe_file):
                return exe_file

    return None
