import os
from gitsvnhelpers.testing import BaseTestCase
from gitsvnhelpers.utils import basename
from gitsvnhelpers.utils import is_git
from gitsvnhelpers.utils import is_git_link
from gitsvnhelpers.utils import is_svn
from gitsvnhelpers.utils import svn_type
from gitsvnhelpers.utils import svn_branch
from gitsvnhelpers.utils import svn_url
from gitsvnhelpers.utils import base_url
from gitsvnhelpers.utils import git_branch
from gitsvnhelpers.gitify import gitify


class TestUtils(BaseTestCase):

    def test_utils_on_trunk(self):
        self.checkout('trunk')
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failIf(is_git_link())
        self.failUnlessEqual(svn_type(), 'trunk')
        self.failUnlessEqual(basename(), 'testpackage')
        self.failUnlessEqual(svn_branch(), 'trunk')
        self.failUnless(svn_url().endswith('/testpackage/trunk'))
        self.failUnless(base_url().endswith('/testpackage/'))

    def test_utils_on_branch(self):
        self.checkout('branches/feature-bar')
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failIf(is_git_link())
        self.failUnlessEqual(svn_type(), 'branches')
        self.failUnlessEqual(basename(), 'testpackage')
        self.failUnlessEqual(svn_branch(), 'feature-bar')
        self.failUnless(svn_url().endswith('/testpackage/branches/feature-bar'))
        self.failUnless(base_url().endswith('/testpackage/'))

    def test_utils_on_tag(self):
        self.checkout('tags/0.1')
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failIf(is_git_link())
        self.failUnlessEqual(svn_type(), 'tags')
        self.failUnlessEqual(basename(), 'testpackage')
        self.failUnlessEqual(svn_branch(), '0.1')
        self.failUnless(svn_url().endswith('/testpackage/tags/0.1'))
        self.failUnless(base_url().endswith('/testpackage/'))

    def test_utils_on_custom_target(self):
        # gitify always works under the assumption, that the package
        # name is the name of the directory it's been invoked in.
        self.checkout('trunk')
        self.failUnlessEqual(basename(), 'testpackage')
        new_checkoutdir = ("%s/trunk" % self.tempdir)
        os.rename(self.checkoutdir, new_checkoutdir)
        self.checkoutdir = new_checkoutdir
        self.failIfEqual(basename(), 'testpackage')

    def test_git_utils_on_trunk(self):
        self.checkout('trunk')
        # before gitification, the branch name is None
        self.assertEqual(git_branch(), None)
        # after gitifcation we expect 'local/trunk' (as per convention)
        gitify(args=['init'])
        self.assertEqual(git_branch(), 'local/trunk')

    def test_git_utils_on_branch(self):
        self.checkout('branches/feature-bar')
        gitify(args=['init'])
        self.assertEqual(git_branch(), 'local/feature-bar')
