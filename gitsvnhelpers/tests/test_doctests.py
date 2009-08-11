import doctest
from jarn.mkrelease.tee import popen
from gitsvnhelpers.testing import BaseTestCase

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)



class TestDoctests(BaseTestCase):

    def shell(self, cmd):
        """executes the shell command and prints its output"""
        code, output = popen(cmd, False, False)
        for line in output:
            print line

    def test_doctests(self):
        for testfile in ['test_gitify.txt',]:
            doctest.testfile(testfile,
                globs=dict(self=self, do=self.shell),
                report=True,
                optionflags=optionflags)