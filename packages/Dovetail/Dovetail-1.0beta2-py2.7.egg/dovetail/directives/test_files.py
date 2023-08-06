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

"""py.test test script for predicates in core.py, environment.py and files.py.

NOTE: Windows file access permissions is, ahem, somewhat different from Posix.
As a result, we test ONLY THE READ BIT.
"""

from files import Access, IsDir, IsFile, IsLink, IsMount, LargerThan, Newer, Which, Glob
from os import path, chmod, access, R_OK, W_OK, X_OK, name as osname, utime
from time import sleep
import stat

BASE = path.abspath(path.join(__file__, "..", "..", "..", "..", "test", "files"))
BASE_PERM = path.join(BASE, "permissions")
BASE_DATA = path.join(BASE, "data")

def set(base, file_name, add=0, remove=0):
    from os import stat as osstat
    file_path = path.join(base, file_name)
    mode = osstat(file_path)[0]
    mode -= mode & remove
    mode |= add
    chmod(file_path, mode)

READ = stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH
WRITE = stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH

#noinspection PyUnusedLocal
def setup_module(module):
    set(BASE_PERM, "read_only",  add=READ,  remove=WRITE)
    set(BASE_PERM, "write_only", add=WRITE, remove=READ)
    set(BASE_PERM, "executable",            remove=READ | WRITE)
    set(BASE_PERM, "private",               remove=READ | WRITE)


#noinspection PyUnusedLocal
def teardown_module(module):
    set(BASE_PERM, "read_only",  add=READ | WRITE)
    set(BASE_PERM, "write_only", add=READ | WRITE)
    set(BASE_PERM, "executable", add=READ | WRITE)
    set(BASE_PERM, "private",    add=READ | WRITE)

class TestFiles(object):

    def test_sanity(self):
        print __file__
        print BASE
        assert access(BASE, R_OK)
        assert path.isdir(BASE)

    def test_access_print(self):
        assert str(Access(BASE, R_OK)).find(BASE) >= 0
        assert str(Access(BASE, R_OK | W_OK | X_OK)).find("R_OK") >= 0
        assert str(Access(BASE, R_OK | W_OK | X_OK)).find("W_OK") >= 0
        assert str(Access(BASE, R_OK | W_OK | X_OK)).find("X_OK") >= 0

    def test_access_base(self):
        assert path.isdir(BASE)
        assert Access(BASE, W_OK)() is True
        if osname != "nt":
            assert Access(BASE, R_OK)() is True
            assert Access(BASE, X_OK)() is True
            assert Access(BASE, R_OK | W_OK | X_OK)() is True

    def test_access_read_only(self):
        name = path.join(BASE_PERM, "read_only")
        assert path.isfile(name)
        assert Access(name, W_OK)() is False
        if osname != "nt":
            assert Access(name, R_OK)() is True
            assert Access(name, X_OK)() is False
        assert Access(name, R_OK | W_OK | X_OK)() is False

    def test_access_write_only(self):
        name = path.join(BASE_PERM, "write_only")
        assert path.isfile(name)
        assert Access(name, W_OK)() is True
        if osname != "nt":
            assert Access(name, R_OK)() is False
            assert Access(name, X_OK)() is False
            assert Access(name, R_OK | W_OK | X_OK)() is False

    def test_access_exec_only(self):
        name = path.join(BASE_PERM, "executable")
        assert path.isfile(name)
        assert Access(name, W_OK)() is False
        if osname != "nt":
            assert Access(name, R_OK)() is False
            assert Access(name, X_OK)() is True
            assert Access(name, R_OK | W_OK | X_OK)() is False

    def test_access_private_only(self):
        name = path.join(BASE_PERM, "private")
        assert path.isfile(name)
        assert Access(name, W_OK)() is False
        if osname != "nt":
            assert Access(name, R_OK)() is False
            assert Access(name, X_OK)() is False
            assert Access(name, R_OK | W_OK | X_OK)() is False

    def test_dir_file(self):
        assert IsDir(BASE_DATA)() is True
        name = path.join(BASE_DATA, "data1.txt")
        assert path.isfile(name)
        assert IsDir (name)() is False
        assert str(IsDir(name)).find(name) >= 0
        assert IsFile(name)() is True
        assert str(IsFile(name)).find(name) >= 0
        assert IsLink(name)() is False
        assert str(IsLink(name)).find(name) >= 0

    def test_larger(self):
        name = path.join(BASE_DATA, "empty")
        assert path.isfile(name)
        assert LargerThan(name     )() is False
        name = path.join(BASE_DATA, "data1.txt")
        assert path.isfile(name)
        assert LargerThan(name     )() is True
        assert LargerThan(name,   5)() is True
        assert LargerThan(name, 100)() is True
        assert LargerThan(name, 200)() is False

    def test_is_mount(self):
        assert IsMount(BASE)() is False
        if osname == "posix":
            assert IsMount("/")() is True
            assert str(IsMount("/")).find("/") >= 0
        elif osname == "nt":
            assert IsMount("C:\\")() is True
            assert str(IsMount("C:\\")).find("C:\\") >= 0

    def test_newer(self):
        n = Newer(Glob(path.join(BASE, "*", "*.txt")),
                  Glob(path.join(BASE, "*", "*.bin")))
        print n
        utime(path.join(BASE_DATA, "out1.bin"), None)
        utime(path.join(BASE_DATA, "out2.bin"), None)
        assert n() is False
        sleep(1)
        utime(path.join(BASE_DATA, "data1.txt"), None)
        assert n() is True
        sleep(1)
        utime(path.join(BASE_DATA, "out1.bin"), None)
        assert n() is True
        sleep(1)
        utime(path.join(BASE_DATA, "out2.bin"), None)
        assert n() is False

    def test_which_predicate(self):

        if osname == "posix":
            app = "ls"
        else:
            app = "cmd.exe"
        p = Which(app)
        assert str(p).find(app) >= 0
        assert p() is True

        p = Which("does.not.exist")
        print p
        assert p() is False
