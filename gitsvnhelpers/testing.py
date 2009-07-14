import shutil
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

    def clone(self, path='trunk'):
        process = Process(quiet=True)
        process.system('svn checkout file://%s/%s %s' % (self.packagedir,
            path, self.source))
        self.clonedir = join(self.tempdir, self.source)
