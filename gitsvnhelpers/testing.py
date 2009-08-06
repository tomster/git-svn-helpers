import shutil
import sys
import StringIO
from os.path import join, dirname
from jarn.mkrelease.testing import SubversionSetup, JailSetup
from jarn.mkrelease.process import Process


class BaseTestCase(SubversionSetup):

    name = 'svn'
    source = 'testrepo.svn'

    def setUp(self):
        JailSetup.setUp(self)
        try:
            package = join(dirname(__file__), 'tests', self.source)
            self.packagedir = join(self.tempdir, 'testpackage')
            shutil.copytree(package, self.packagedir)
        except:
            self.cleanUp()
            raise

    def checkout(self, path='trunk'):
        process = Process(quiet=True)
        process.system('svn checkout file://%s/%s %s' % (self.packagedir,
            path, self.source))
        self.checkoutdir = join(self.tempdir, self.source)


class StdOut(StringIO.StringIO):
    """ A StringIO based stdout replacement that optionally mirrors all
        output to stdout in addition to capturing it.
    """

    def __init__(self, stdout):
        self.__stdout = stdout
        StringIO.StringIO.__init__(self)

    def write(self, s):
        # uncomment the following for debugging tests!
        # #self.__stdout.write(s)
        StringIO.StringIO.write(self, s)

    def read(self):
        self.seek(0)
        self.__stdout.write(StringIO.StringIO.read(self))


class CommandTestCase(BaseTestCase):
    """ a test class that captures stdout and stderr and points GIT_CACHE
        to a temporary directory
    """

    def setUp(self):
        BaseTestCase.setUp(self)
        config.GIT_CACHE = join(self.tempdir, '.gitcache/')
        self.out = StdOut(sys.stdout)
        self.err = StdOut(sys.stdout)
        sys.stdout = self.out
        sys.stderr = self.err

    def cleanUp(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
