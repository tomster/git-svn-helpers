import shutil
import sys
import os
import StringIO
from os.path import join, dirname
from jarn.mkrelease.testing import SubversionSetup, JailSetup, GitSetup
from jarn.mkrelease.process import Process
from gitsvnhelpers import config


class BaseTestCase(SubversionSetup):

    name = 'svn'
    source = 'testrepo.svn'
    packagename = 'testpackage'

    def setUp(self):
        JailSetup.setUp(self)
        # monkeypatch GIT_CACHE to point to a temporary directory
        config.GIT_CACHE = join(self.tempdir, '.gitcache/')
        # copy the test repo to temp, we perform all checkouts from there:
        try:
            original_repo = join(dirname(__file__), 'tests', self.source)
            # the target folder needs to be the packagename, so that the
            # file:/// urls used throughout testing match the pacakge name
            # normally, the filesystem name doesn't matter, when it's being
            # served via http
            os.mkdir("%s/repos/" % self.tempdir)
            self.repo = join(self.tempdir, 'repos', self.packagename)
            shutil.copytree(original_repo, self.repo)
        except:
            self.cleanUp()
            raise

    def checkout(self, path='trunk', target=None):
        process = Process(quiet=True)
        if target is None:
            self.checkoutdir = join(self.tempdir, self.packagename)
        else:
            self.checkoutdir = join(self.tempdir, target, self.packagename)
        process.system('svn checkout file://%s/%s %s' % (self.repo,
            path, self.checkoutdir))
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
    source = 'testrepo.git'

    def setUp(self):
        JailSetup.setUp(self)
        try:
            package = join(dirname(__file__), 'tests', self.source)
            self.packagedir = join(self.tempdir, 'testpackage')
            shutil.copytree(package, self.packagedir)
            os.chdir(self.packagedir)
        except:
            self.cleanUp()
            raise
