import os

from gitsvnhelpers.testing import BaseTestCase
from gitsvnhelpers.utils import basename
from gitsvnhelpers.utils import is_git
from gitsvnhelpers.utils import is_svn
from gitsvnhelpers.utils import svn_type
from gitsvnhelpers.utils import svn_branch
from gitsvnhelpers.utils import svn_url
from gitsvnhelpers.utils import base_url


class TestUtils(BaseTestCase):

    def test_utils_on_trunk(self):
        self.clone()
        os.chdir(self.clonedir)
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failUnlessEqual(svn_type(), 'trunk')
        self.failUnlessEqual(basename(), 'testrepo.svn')
        self.failUnlessEqual(svn_branch(), 'trunk')
        self.failUnless(svn_url().endswith('/testpackage/trunk'))
        self.failUnless(base_url().endswith('/testpackage/'))

    def test_utils_on_branch(self):
        self.clone('branches/feature-bar')
        os.chdir(self.clonedir)
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failUnlessEqual(svn_type(), 'branches')
        self.failUnlessEqual(basename(), 'testrepo.svn')
        self.failUnlessEqual(svn_branch(), 'feature-bar')
        self.failUnless(svn_url().endswith('branches/feature-bar'))
        self.failUnless(base_url().endswith('/testpackage/'))
