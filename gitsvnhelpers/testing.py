import sys
import os
import StringIO
from os.path import join
import subprocess

from jarn.mkrelease.testing import SubversionSetup, JailSetup, GitSetup
from gitsvnhelpers import config


class BaseTestCase(SubversionSetup):

    name = 'svn'
    packagename = 'testpackage'

    def setUp(self):
        JailSetup.setUp(self)
        # monkeypatch GIT_CACHE to point to a temporary directory
        config.GIT_CACHE = join(self.tempdir, '.gitcache/')
        # copy the test repo to temp, we perform all checkouts from there:
        try:
            # the target folder needs to be the packagename, so that the
            # file:/// urls used throughout testing match the pacakge name
            # normally, the filesystem name doesn't matter, when it's being
            # served via http
            os.mkdir(join(self.tempdir, "repos"))
            self.repo = join(self.tempdir, 'repos', self.packagename)
            subprocess.check_call(["svnadmin", "create", self.repo])
            subprocess.check_call(
                ["svn", "mkdir", "-m", "repo layout"]
                +["file://%s/%s" % (self.repo, folder)
                  for folder in ('trunk', 'branches', 'tags')],
                stdout=subprocess.PIPE)

            self.checkout(target="setUp")
            open('README.txt', 'w').write("Package documentation\n")
            subprocess.check_call(["svn", "add", "README.txt"],
                                  stdout=subprocess.PIPE)
            subprocess.check_call(["svn", "commit", "-m", "Begin docs"],
                                  stdout=subprocess.PIPE)

            open('foo.py', 'w').write('"""fooberizing"""\n')
            subprocess.check_call(["svn", "add", "foo.py"],
                                  stdout=subprocess.PIPE)
            subprocess.check_call(
                ["svn", "commit", "-m", "First attempt at fooberizing"],
                stdout=subprocess.PIPE)
            subprocess.check_call(["svn", "copy", "-m", "Release 0.1",
                                   "file://%s/trunk" % self.repo,
                                   "file://%s/tags/0.1" % self.repo],
                                  stdout=subprocess.PIPE)

            subprocess.check_call(
                ["svn", "copy", "-m", "Begin work on feature bar",
                 "file://%s/trunk" % self.repo,
                 "file://%s/branches/feature-bar" % self.repo],
                stdout=subprocess.PIPE)
            subprocess.check_call(
                ["svn", "switch",
                 "file://%s/branches/feature-bar" % self.repo],
                stdout=subprocess.PIPE)
            open('README.txt', 'a').write("Now supports bar\n")
            open('foo.py', 'a').write('import bar\n')
            open('bar.py', 'w').write('"""barberizing"""\n')
            subprocess.check_call(["svn", "add", "bar.py"],
                                  stdout=subprocess.PIPE)
            subprocess.check_call(
                ["svn", "commit", "-m", "Implement bar feature"],
                stdout=subprocess.PIPE)
        except:
            self.cleanUp()
            raise

    def checkout(self, path='trunk', target=None):
        if target is None:
            self.checkoutdir = join(self.tempdir, self.packagename)
        else:
            self.checkoutdir = join(self.tempdir, target, self.packagename)
        args = ['svn', 'checkout', 'file://%s/%s' % (self.repo, path),
                '%s' % self.checkoutdir]
        subprocess.check_call(args, stdout=subprocess.PIPE)
        os.chdir(self.checkoutdir)


class StdOut(StringIO.StringIO):
    """ A StringIO based stdout replacement that optionally mirrors all
        output to stdout in addition to capturing it.
    """

    def __init__(self, stdout):
        self.__stdout = stdout
        StringIO.StringIO.__init__(self)

    def write(self, s):
        # uncomment the following for debugging tests!
        # self.__stdout.write(s)
        StringIO.StringIO.write(self, s)

    def read(self):
        self.seek(0)
        self.__stdout.write(StringIO.StringIO.read(self))


class CommandTestCase(BaseTestCase):
    """ a test class that captures stdout and stderr
    """

    def setUp(self):
        BaseTestCase.setUp(self)
        self.out = StdOut(sys.stdout)
        self.err = StdOut(sys.stdout)
        sys.stdout = self.out
        sys.stderr = self.err

    def cleanUp(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class GitTestCase(GitSetup):
    """ a test class that operates on a git repository
    """

    def setUp(self):
        JailSetup.setUp(self)
        try:
            self.packagedir = join(self.tempdir, 'testpackage')
            os.mkdir(self.packagedir)
            os.chdir(self.packagedir)
            subprocess.check_call(['git', 'init'], stdout=subprocess.PIPE)
        except:
            self.cleanUp()
            raise
