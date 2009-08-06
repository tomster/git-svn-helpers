from gitsvnhelpers.testing import CommandTestCase
from gitsvnhelpers.gitify import gitify


class TestGitify(CommandTestCase):

    def test_args(self):
        self.assertRaises(SystemExit, gitify, args=['xxxx'])
        self.failUnless("Unknown command 'xxxx'" in self.err.getvalue())
        gitify(args=['help'])
        self.failUnless("usage" in self.out.getvalue())
