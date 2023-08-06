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

"""Version and product information constants"""
from os import path

def read(filename):
    """Returns the contants of the file as a string"""
    return open(path.join(path.dirname(__file__), filename)).read()

VERSION = "1.0beta3"
"""The version of Dovetail, for setup.py"""

DEVELOPMENT_STATUS = "Development Status :: 4 - Beta"
"""Development status for setup.py"""

DESCRIPTION = "Dovetail: A light-weight, multi-platform build tool with Continuous Integration servers like Jenkins in mind"
"""Description of Dovetail for setup.py"""

USAGE = read("USAGE.rst") + "\n" + read('NOTICE.txt')

EPILOG = read('NOTICE.txt')

WARRANTY = read("WARRANTY.txt")

LICENSE = read("LICENSE.txt")
