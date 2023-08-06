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

"""py.test test script for packages.py"""

import packages
#noinspection PyPackageRequirements
import pytest
from pkg_resources import VersionConflict

SD    = ["sooperdooper"]
PL    = ["pylint"]
GOOD  = ["pylint", "coverage"]
BAD   = ["pylint", "coverage", "sooperdooper"]
MANYB = ["silly1", "silly2", "silly3"]
ERR   = ["pylint>1000"]

#noinspection PyUnusedLocal
def setup_module(module):
    packages.install(GOOD)


#noinspection PyUnresolvedReferences
class TestModules(object):

    def test_install(self):
        packages.install(PL)
        packages.install(GOOD)

    def test_cannot_install(self):
        with pytest.raises(packages.MissingRequirement):
            packages.install( BAD )

    def test_present(self):
        assert not packages.not_present(GOOD)

    def test_not_present(self):
        assert SD == packages.not_present(SD)

    def test_mixed(self):
        assert SD == packages.not_present(BAD)


    def test_multiple_not_present(self):
        assert MANYB == packages.not_present(MANYB, stop_on_error=False)
        assert ERR == packages.not_present(ERR, stop_on_error=False)

    def test_version_conflict(self):
        packages.install(PL)
        with pytest.raises(VersionConflict):
            packages.not_present(["pylint>1000"])

    def test_predicate(self):
        i = packages.Installed(*PL)
        print i
        assert i() is True

        i = packages.Installed(*GOOD)
        print i
        assert i() is True

        i = packages.Installed(*BAD)
        print i
        assert i() is False
