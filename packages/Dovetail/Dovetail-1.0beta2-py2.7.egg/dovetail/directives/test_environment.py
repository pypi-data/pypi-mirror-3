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

"""py.test test script for environment.py"""

from environment import apply_environment, revert_environment
from environment import pp_adjust_env, Env, EnvRE
from os import environ

ENV1 = "TEST_ENV_1"
ENV2 = "TEST_ENV_2"
ENV3 = "TEST_ENV_3"
ENV4 = "TEST_ENV_4"
ENV5 = "TEST_ENV_5"
ENV_KEYS = [ ENV1, ENV2, ENV3, ENV4, ENV5 ]
ENV_ADDS = {}
ENV_REMOVES = {}
BAD1 = "BAD1"
BAD2 = "BAD2"

def filter(d):
    """Filters a dictionary to include only those keys we are testing for"""
    return { k:v for k, v in d.iteritems() if k in ENV_KEYS }

def setup_module():
    for key in ENV_KEYS:
        ENV_ADDS[key] = "Value " + key
    for key in ENV_KEYS:
        ENV_REMOVES[key] = None
    for env in ENV_KEYS:
        try:
            del environ[env]
        except KeyError:
            pass

class TestEnvironment(object):
    def testApplyNothing(self):
        orig = environ.copy()
        assert {} == apply_environment({})
        assert orig == environ

    def testRevertNothing(self):
        orig = environ.copy()
        revert_environment({})
        assert orig == environ

    def testApplyAddition(self):
        orig = environ.copy()
        new  = orig.copy()
        for k, v in ENV_ADDS.iteritems():
            new[k] = v

        memento = apply_environment(ENV_ADDS)
        assert filter(new) == filter(environ)

        revert_environment(memento)
        assert filter(orig) == filter(environ)

    def testRemoveVariables(self):
        apply_environment(ENV_ADDS)

        environ.copy()
        memento = apply_environment(ENV_REMOVES)

        assert ENV_ADDS == memento
        assert {} == filter(environ)

    def testApplyModification(self):
        apply_environment(ENV_ADDS)

        orig = environ.copy()
        memento = apply_environment({ENV1:'changed', 'NEW':'new'})
        revert_environment(memento)
        assert orig == environ


    def test_pp_adjust(self):
        assert ''                                                == pp_adjust_env({})
        assert 'unsetting TEST_ENV_1'                            == pp_adjust_env({ENV1:None})
        assert 'unsetting TEST_ENV_2, TEST_ENV_1'                == pp_adjust_env({ENV1:None, ENV2:None})
        assert 'setting TEST_ENV_1="1"'                          == pp_adjust_env({ENV1:'1'})
        assert 'setting TEST_ENV_2="2", TEST_ENV_1="1"'          == pp_adjust_env({ENV1:'1', ENV2:'2'})
        assert 'setting TEST_ENV_2="2" and unsetting TEST_ENV_1' == pp_adjust_env({ENV1:None, ENV2:'2'})

    def test_pp_test(self):
        assert ''                                       == str(Env())
        assert '$TEST_ENV_1 is set'                     == str(Env(ENV1))
        assert '$TEST_ENV_2, $TEST_ENV_1 are set'       == str(Env(ENV1, ENV2))
        assert '$TEST_ENV_1="1"'                        == str(Env(TEST_ENV_1='1'))
        assert '$TEST_ENV_2="2", $TEST_ENV_1="1"'       == str(Env(TEST_ENV_1='1', TEST_ENV_2='2'))
        assert '$TEST_ENV_2="2" and $TEST_ENV_1 is set' == str(Env(ENV1, TEST_ENV_2='2'))

    def test_env_predicate(self):
        assert Env(ENV1)() is True
        assert Env(ENV1, ENV2)() is True
        assert Env(BAD1)() is False
        assert Env(BAD1, BAD2)() is False
        assert Env(TEST_ENV_2='Value TEST_ENV_2')() is True
        assert Env(TEST_ENV_1='Value TEST_ENV_1', TEST_ENV_2='Value TEST_ENV_2')() is True
        assert Env(TEST_ENV_2='BAD')() is False
        assert Env(TEST_ENV_1='BAD', TEST_ENV_2='BAD')() is False
        assert Env(ENV1, ENV2, TEST_ENV_2='Value TEST_ENV_2')() is True
        assert Env(ENV1, BAD2, TEST_ENV_2='Value TEST_ENV_2')() is False

    def test_env_re_predicate(self):
        assert EnvRE(TEST_ENV_1="ENV")() is True
        assert EnvRE(TEST_ENV_1="^Value")() is True
        assert EnvRE(TEST_ENV_1="NOT")() is False
        assert EnvRE(TEST_ENV_1="_1$")() is True
        assert EnvRE(TEST_ENV_1="^Value [A-Z]+_[A-Z]+_[0-9]+$")() is True
        assert EnvRE(TEST_ENV_1="ENV", TEST_ENV_2="^Value")() is True
        assert EnvRE(BAD1=".*")() is False