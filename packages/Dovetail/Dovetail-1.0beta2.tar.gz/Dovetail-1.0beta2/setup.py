"""Distutils setup script for Dovetail.

Dovetail: A light-weight, multi-platform, build tool for Python with
          Continuous Integration servers like Jenkins in mind.
Copyright (C) 2012, Aviser LLP, Singapore.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from os import path
from datetime import datetime
from setuptools import setup, find_packages
from dovetail.constants import VERSION, DEVELOPMENT_STATUS

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

NOW = datetime.now().replace(microsecond=0)
LONG_DESCRIPTION = read(path.join("..", "README.rst"))

# Commented for initial release
#if "JENKINS_HOME" in environ:
#    # We are being built in Jenkins
#    VCS_VER     = os.environ['MERCURIAL_REVISION']
#    BUILD       = os.environ['JOB_NAME']
#    BUILD_NUM   = os.environ['BUILD_NUMBER']
#    FULLVERSION = VERSION + "b" + BUILD_NUM
#    LONG_DESCRIPTION += """\
#Build host/arch:   {0}/{1}
#Build name/number: {2}/{3}
#Build date/time:   {4}
#Commit:            {5}
#""".format(socket.gethostname(), get_build_platform(),
#           BUILD, NOW.isoformat(),
#           os.environ['BUILD_ID'],
#           VCS_VER)
#else:
#    # Manual build
#    VCS_VER     = 'dev'
#    BUILD       = 'Dovetail'
#    FULLVERSION = VERSION + "dev"
#    LONG_DESCRIPTION += """\
#DEVELOPMENT BUILD
#User@Host:         {0}@{1}
#Build arch:        {2}
#Build date/time:   {3}
#""".format(getpass.getuser(), socket.gethostname(),
#           get_build_platform(),
#           NOW.isoformat())
FULL_VERSION = VERSION

setup(
    name='Dovetail',
    version=FULL_VERSION,
    description='A light-weight, multi-platform, build tool for Python with \
    Continuous Integration servers like Jenkins in mind.',
    long_description=LONG_DESCRIPTION,
    author='Andrew Alcock, Aviser LLP, Singapore',
    author_email='dovetail@aviser.asia',
    url='http://www.aviser.asia/dovetail',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        DEVELOPMENT_STATUS,
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        ],
    keywords='build, continuous integration, ci',
    license='GPLv3+',

    # The main definition of the installer
    packages=find_packages(exclude=["test"]),
    package_data = { '':['*.txt', '*.rst'] },

    entry_points = {
        'console_scripts': [
            'dovetail  = dovetail.main:main'
        ],
    },
    install_requires=["setuptools>=0.6c"],
    extras_require = { 'virtualenv': ['virtualenv>=1.6.2']}
    )

