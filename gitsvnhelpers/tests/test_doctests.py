import doctest
from jarn.mkrelease.tee import popen
from gitsvnhelpers.testing import BaseTestCase

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)



class TestDoctests(BaseTestCase):

    def runTest(self):
        raise NotImplemented

    def shell(self, cmd):
        """executes the shell command and prints its output"""
        code, output = popen(cmd, False, False)
        for line in output:
            print line


def setUp(test):
    self = TestDoctests()
    test.globs.update(self=self, do=self.shell)
    self.setUp()


def tearDown(test):
    test.globs['self'].tearDown()


def test_suite():
    return doctest.DocFileSuite(
        'test_gitify.txt',
        'test_gitify_up.txt',
        'test_gitify_fetch.txt',
        'test_symlink_migration.txt',
        'test_svn_switch.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=optionflags)
