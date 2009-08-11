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

    def _test_doctest(self):
        doctest.testfile("%s.txt" % self._testMethodName,
            globs=dict(self=self, do=self.shell),
            report=True,
            optionflags=optionflags)

    def test_gitify(self):
        self._test_doctest()

    def test_gitify_up(self):
        self._test_doctest()

