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

"""py.test test script for utilities.py"""

from utilities import enum

#noinspection PyPackageRequirements
import pytest

#noinspection PyUnresolvedReferences
class TestEnum:
    enumeration = enum(ONE=1, TWO=2, THREE=3, FOUR='four')

    def test_basics(self):
        assert 1      == TestEnum.enumeration.ONE
        assert 2      == TestEnum.enumeration.TWO
        assert 3      == TestEnum.enumeration.THREE
        assert 'four' == TestEnum.enumeration.FOUR

    def test_as_str(self):
        assert 'ONE'   == TestEnum.enumeration.as_str(TestEnum.enumeration.ONE)
        assert 'TWO'   == TestEnum.enumeration.as_str(TestEnum.enumeration.TWO)
        assert 'THREE' == TestEnum.enumeration.as_str(TestEnum.enumeration.THREE)
        assert 'FOUR'  == TestEnum.enumeration.as_str(TestEnum.enumeration.FOUR)

    def test_lookup(self):
        assert TestEnum.enumeration.ONE   == TestEnum.enumeration.lookup('ONE')
        assert TestEnum.enumeration.TWO   == TestEnum.enumeration.lookup('TWO')
        assert TestEnum.enumeration.THREE == TestEnum.enumeration.lookup('THREE')
        assert TestEnum.enumeration.FOUR  == TestEnum.enumeration.lookup('FOUR')

    def test_lookup_miss(self):
        with pytest.raises(KeyError):
            TestEnum.enumeration.lookup('NOT_HERE')

    def test_as_str_miss(self):
        with pytest.raises(KeyError):
            TestEnum.enumeration.as_str('NOT_HERE')

    def test_names(self):
        assert set(TestEnum.enumeration.names()) == {"ONE", "TWO", "THREE", "FOUR"}
