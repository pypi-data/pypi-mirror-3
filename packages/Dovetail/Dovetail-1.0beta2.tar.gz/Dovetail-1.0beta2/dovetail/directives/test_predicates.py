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

"""py.test test script for predicates in core.py, environment.py and files.py"""

from core import Any, All, Not

class AlwaysTrue(object):
    def __call__(self):
        return True
    def __str__(self):
        return "True"


class AlwaysFalse(object):
    def __call__(self):
        return False
    def __str__(self):
        return "False"

TRUE = AlwaysTrue()
FALSE = AlwaysFalse()

def always_true():
    return True

def always_false():
    return False

class TestLogic(object):

    def test_basics(self):
        """Make sure primitives work"""
        assert AlwaysTrue()() is True
        assert AlwaysFalse()() is False

    def test_any(self):
        assert Any()() is False
        assert Any(TRUE)() is True
        assert Any(FALSE)() is False
        assert Any(FALSE, FALSE, FALSE)() is False
        assert Any(TRUE, FALSE)() is True
        assert Any(FALSE, TRUE)() is True
        assert Any(FALSE, FALSE, FALSE, TRUE, FALSE, FALSE)() is True
        assert str(Any(TRUE)).startswith("Any(")
        assert str(Any(TRUE)).endswith(")")

    def test_all(self):
        assert All()() is True
        assert All(TRUE)() is True
        assert All(FALSE)() is False
        assert All(TRUE, TRUE, TRUE)() is True
        assert All(TRUE, FALSE)() is False
        assert All(TRUE, FALSE, TRUE)() is False
        assert All(TRUE, TRUE, FALSE, TRUE, TRUE, TRUE)() is False
        assert All(TRUE, TRUE, TRUE, TRUE, TRUE)() is True
        assert str(All(TRUE)).startswith("All(")
        assert str(All(TRUE)).endswith(")")

    def test_not(self):
        assert Not(TRUE)() is False
        assert Not(FALSE)() is True
        assert str(Not(TRUE)).startswith("Not(")
        assert str(Not(TRUE)).endswith(")")

    def test_predicate_function(self):
        assert Not(always_true)() is False
        assert Not(always_false)() is True
        assert All(always_true)() is True
        assert All(always_false)() is False
        assert Any(always_true)() is True
        assert Any(always_false)() is False