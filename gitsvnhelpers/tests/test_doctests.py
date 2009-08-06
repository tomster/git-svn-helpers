import doctest
from gitsvnhelpers.testing import BaseTestCase
from gitsvnhelpers.testing import CommandTestCase

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)



class TestDoctests(CommandTestCase):

    def test_doctests(self):
        for testfile in ['test_gitify.txt',]:
            doctest.testfile(testfile,
                globs=dict(self=self),
                report=True,
                optionflags=optionflags)