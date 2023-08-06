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

"""Environment-based directives."""

# This class implements functions declared elsewhere and
# cannot control the arguments
# pylint: disable-msg=W0613
# The classes in this file are deliberately simple
# pylint: disable-msg=R0903

from dovetail.model import TaskWrapper
from dovetail.util import Logger

from os import environ
import re

def unset(key):
    """Unset an environment variable using del environ[key], ignoring
    any KeyError"""
    try:
        del environ[key]
    except KeyError:
        pass

def apply_environment(environment):
    """Internal method that applies a dictionary of values to the
    :obj:`os.environ` while recording the original values.

    :param environment: A :ref:`modification_dictionary` that will be applied\
                        to :obj:`os.environ`.
    :type environment: dict
    :return: an object which, when passed to :func:`revert_environment`, will
             reset the environment variables modified by this function"""
    memento = {}
    for name, value in environment.iteritems():
        try:
            memento[name] = environ[name]
        except KeyError:
            memento[name] = None
        if value is None:
            Logger.debug("Unsetting environment variable: {0}".format(name))
            unset(name)
        else:
            Logger.debug("Setting environment variable: {0}={1}".format(name, value))
            environ[name] = value
    return memento

def revert_environment(memento):
    """Resets the environment variables modified by :func:`apply_environment`.

    :param memento: The return value from :func:`apply_environment`

    .. warning::

       Other environment variables modified after the call to
       :func:`apply_environment` and :func:`revert_environment` will be left unchanged.

    .. warning::

       If several 'nested' snapshots are takes, they must be reverted in the
       inverse order, otherwise the environment may not be restored as expected"""
    for name, value in memento.iteritems():
        if value is None:
            Logger.debug("Resetting environment variable: {0}=".format(name))
            unset(name)
        else:
            Logger.debug("Resetting environment variable: {0}={1}".format(name, memento[name]))
            environ[name] = memento[name]

def pp_adjust_env(environment):
    """Pretty-print a :ref:`modification_dictionary`.

    :param environment: The modification dictionary to print
    :type environment: dict"""
    been_unset = [ k for k, v in environment.iteritems() if v is None ]
    if been_unset:
        been_unset = "unsetting " + ", ".join(been_unset)
    else:
        been_unset = None

    been_set   = [ '{0}="{1}"'.format(k, v) for k, v in environment.iteritems() if v is not None ]
    if been_set:
        been_set = "setting " + ", ".join(been_set)
    else:
        been_set = None
    if been_set is None and been_unset is None:
        return ""
    elif been_set is None:
        return been_unset
    elif been_unset is None:
        return been_set
    else:
        return " and ".join([been_set, been_unset])

def adjust_env(*remove, **merge):
    """Temporarily sets environment variables for the duration of the decorated function.

    :param remove: Environment variables to unset
    :type remove:  string
    :param merge:  List of environment variables to set, the argument name being\
                   mapped to the environment variable name
    :type merge:   string

    The parameters are more fully described in :ref:`environment_arguments`.

    For example::

        @adjust_env("REMOVE", NEW='value')

    will unset $REMOVE and set $NEW to 'value'.

    All environment variables are reset to their original values at the end of the
    task even if the calling function modified their value. Other
    modifications to the environment (for example new variables) are preserved."""
    assert not any((k, v) for k, v in merge.iteritems()
                            if v is not None and not isinstance(v, basestring))
    assert not any(k for k in remove
                            if not isinstance(k, basestring))

    environment = merge.copy()
    for key in remove:
        environment[key] = None

    def before(execution):
        Logger.log("@adjust_env: Modifying os.environ: {0}".format(pp_adjust_env(environment)))
        execution.store(adjust_env, apply_environment(environment))


    #noinspection PyUnusedLocal
    def after(execution, result):
        Logger.log("@adjust_env: Reverting os.environ")
        revert_environment(execution.retrieve(adjust_env))

    return TaskWrapper.decorator_maker("@adjust_env", before=before, after=after)

class Env(object):
    """A predicate that returns True if the environment meets all the specified criteria.

    :param if_set: List of environment variables to test to see if they exist
    :param if_equals: List of environment variable equality tests
    :rtype: boolean

    The **if_set** and **if_equals** parameters are more fully described
    at :ref:`modification_dictionary`.
     """
    def __init__(self, *if_set, **if_equals):
        assert not any((k, v) for k, v in if_equals.iteritems()
                                if v is not None and not isinstance(v, basestring))
        assert not any(k for k in if_set
                         if not isinstance(k, basestring))

        self.tests = if_equals.copy()
        for key in if_set:
            self.tests[key] = None

        self.description = self._pp_test_env()

    def __call__(self):
        for key, value in self.tests.iteritems():
            if value is None:
                if environ.has_key(key):
                    Logger.debug("Env: ${0} is set? True".format(key))
                else:
                    Logger.debug("Env: ${0} is unset? False".format(key))
                    return False
            else:
                if environ.has_key(key) and environ[key] == value:
                    Logger.debug('Env: ${0}="{1}"? True'.format(key, value))
                else:
                    Logger.debug('Env: ${0}="{1}"? False'.format(key, value))
                    return False
        return True


    def _pp_test_env(self):
        """Pretty-print the environment modification dictionary"""
        been_unset = [ "$" + k for k, v in self.tests.iteritems() if v is None ]
        if been_unset:
            if len(been_unset) == 1:
                desc = " is set"
            else:
                desc = " are set"
            been_unset = ", ".join(been_unset) + desc
        else:
            been_unset = None

        been_set = [ '${0}="{1}"'.format(k, v) for k, v in self.tests.iteritems()
                        if v is not None ]
        if been_set:
            been_set = ", ".join(been_set)
        else:
            been_set = None
        if been_set is None and been_unset is None:
            return ""
        elif been_set is None:
            return been_unset
        elif been_unset is None:
            return been_set
        else:
            return " and ".join([been_set, been_unset])

    def __str__(self):
        return self.description

class EnvRE(object):
    """A Predicate for testing environment variables against regular
    expressions.

    :param tests: List of NAME=RE arguments where NAME is the environment\
                  variable to be checked, and RE is the regular expression
    :type tests: string
    :rtype: boolean

    The Python :func:`re.search` method is used, rather than :func:`re.match`,
    so the whole value of the environment variable is tested, rather than just
    the anchoring the search to the beginning of the value.

    Examples::

        >>> predicate = EnvRE(DOVETAIL_NODE="mercury")

    A predicate that matches hostnames of mercury.example.com,
    mercuryrising.example.org, www.mercury.ru, etc

    ::

        >>> predicate = EnvRE(DOVETAIL_NODE="mercury.*")

    Same as previous

    ::

        >>> predicate = EnvRE(DOVETAIL_NODE="^mercury\.")

    A predicate that matches the host "mercury" in any domain.

    ::

        >>> predicate = EnvRE(DOVETAIL_NODE="\.example\.com$")

    A predicate than matches hosts in any subdomain of example.com

    ::

        >>> predicate = EnvRE(A="^start", B="end$")

    A predicate that returns True if the value of A starts with 'start' and
    the value of B ends with 'end'
    """
    def __init__(self, **tests):
        assert len(tests) > 0
        assert not any((k, v) for k, v in tests.iteritems()
                                if v is not None and not isinstance(v, basestring))
        self.tests    = tests
        self.compiled = {}
        for key, expression in tests.iteritems():
            self.compiled[key] = re.compile(expression)

        description = [ '${0}=~"{1}"'.format(k, v) for k, v
                                    in self.tests.iteritems() if v is not None ]
        self.description = "RE search: (" + " and ".join(description) + ")"

    def __call__(self):
        for key, expression in self.compiled.iteritems():
            if environ.has_key(key):
                value = environ[key]
                hits = expression.search(value)
                Logger.debug('EnvRE on ${0}: "{1}"=~"{2}"? {3}'.
                                format(key, value, self.tests[key], hits is not None))
                if hits is None:
                    return False
            else:
                Logger.debug('EnvRE: ${0} is not set. Return False'.format(key))
                return False
        return True


    def _pp_test_env(self):
        """Pretty-print the environment modification dictionary"""


    def __str__(self):
        return self.description

