import sys
import os
import unittest
import tempfile
import shutil
import StringIO

from os.path import realpath, join, dirname, isdir

from jarn.mkrelease.process import Process
from jarn.mkrelease.dirstack import DirStack, chdir


class JailSetup(unittest.TestCase):
    """Manage a temporary working directory."""

    dirstack = None
    tempdir = None

    def setUp(self):
        self.dirstack = DirStack()
        try:
            self.tempdir = realpath(self.mkdtemp())
            self.dirstack.push(self.tempdir)
        except:
            self.cleanUp()
            raise

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.dirstack is not None:
            while self.dirstack:
                self.dirstack.pop()
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)

    def mkdtemp(self):
        return tempfile.mkdtemp()


class PackageSetup(JailSetup):
    """Make sure the jail contains a testpackage."""

    source = None
    packagedir = None

    def setUp(self):
        JailSetup.setUp(self)
        try:
            package = join(dirname(__file__), 'tests', self.source)
            self.packagedir = join(self.tempdir, 'testpackage')
            shutil.copytree(package, self.packagedir)
        except:
            self.cleanUp()
            raise


class PackageAPI(PackageSetup):
    """API for manipulating the sandbox."""

    name = ''
    clonedir = None
    auto_clone = False

    def clone(self):
        raise NotImplementedError

    def setUp(self):
        PackageSetup.setUp(self)
        if self.auto_clone:
            try:
                self.clone()
            except:
                self.cleanUp()
                raise

    def destroy(self, dir=None, name=None):
        if dir is None:
            dir = self.packagedir
        if name is None:
            name = self.name
        if name:
            if name == 'svn':
                self._destroy_svn(dir, name)
            else:
                shutil.rmtree(join(dir, '.'+name))

    def _destroy_svn(self, dir, name):
        if isdir(join(dir, 'db', 'revs')): # The svn repo
            shutil.rmtree(join(dir, 'db'))
        else:
            for path, dirs, files in os.walk(dir):
                if '.svn' in dirs:
                    shutil.rmtree(join(path, '.svn'))
                    dirs.remove('.svn')

    def modify(self, dir):
        appendlines(join(dir, 'setup.py'), ['#foo'])

    def verify(self, dir):
        line = readlines(join(dir, 'setup.py'))[-1]
        self.assertEqual(line, '#foo')

    def delete(self, dir):
        os.remove(join(dir, 'setup.py'))

    def remove(self, dir):
        raise NotImplementedError

    def update(self, dir):
        raise NotImplementedError

    def tag(self, dir, tagid):
        raise NotImplementedError


class SubversionSetup(PackageAPI):
    """Set up a Subversion sandbox."""

    name = 'svn'
    source = 'testrepo.svn'
    auto_clone = True

    def clone(self):
        process = Process(quiet=True)
        process.system('svn checkout file://%s/trunk testclone' % self.packagedir)
        self.clonedir = join(self.tempdir, 'testclone')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('svn remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('svn update')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('svn cp -m"Tag" file://%s/trunk %s' % (self.packagedir, tagid))


class MercurialSetup(PackageAPI):
    """Set up a Mercurial sandbox."""

    name = 'hg'
    source = 'testpackage.hg'
    auto_clone = False

    def clone(self):
        process = Process(quiet=True)
        process.system('hg clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('hg remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('hg update')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('hg tag %s' % tagid)


class GitSetup(PackageAPI):
    """Set up a Git sandbox."""

    name = 'git'
    source = 'testpackage.git'
    auto_clone = False

    def clone(self):
        process = Process(quiet=True)
        process.system('git clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')
        # Park the server on a branch because "Updating the currently checked
        # out branch may cause confusion..."
        self.dirstack.push('testpackage')
        process.system('git checkout -b parking')
        self.dirstack.pop()

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('git rm setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('git checkout master')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('git tag %s' % tagid)


class MockProcessError(Exception):
    """Raised by MockProcess."""


class MockProcess(Process):
    """A Process we can tell what to return by

    - passing rc and lines, or
    - passing a function that returns rc and lines depending on cmd.
    """

    def __init__(self, rc=None, lines=None, func=None):
        Process.__init__(self, quiet=True)
        self.rc = rc or 0
        self.lines = lines or []
        self.func = func

    def popen(self, cmd, echo=True, echo2=True):
        if self.func is not None:
            rc_lines = self.func(cmd)
            if rc_lines is not None:
                return rc_lines
            else:
                raise MockProcessError('Unhandled command: %s' % cmd)
        return self.rc, self.lines

    def os_system(self, cmd):
        if self.func is not None:
            rc_lines = self.func(cmd)
            if rc_lines is not None:
                return rc_lines[0]
            else:
                raise MockProcessError('Unhandled command: %s' % cmd)
        return self.rc


def quiet(func):
    """Decorator swallowing stdout and stderr output.
    """
    def wrapped_func(*args, **kw):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO.StringIO()
        try:
            return func(*args, **kw)
        finally:
            sys.stdout, sys.stderr = saved

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func


def readlines(filename):
    """Read lines from file 'filename'.

    Lines are not newline terminated.
    """
    f = open(filename, 'rb')
    try:
        return f.read().strip().replace('\r', '\n').split('\n')
    finally:
        f.close()


def appendlines(filename, lines):
    """Append 'lines' to file 'filename'.
    """
    f = open(filename, 'at')
    try:
        for line in lines:
            f.write(line+'\n')
    finally:
        f.close()

