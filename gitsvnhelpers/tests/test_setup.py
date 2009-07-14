import os

from gitsvnhelpers.testing import BaseTestCase
from gitsvnhelpers.utils import basename
from gitsvnhelpers.utils import is_git
from gitsvnhelpers.utils import is_svn
from gitsvnhelpers.utils import svn_type
from gitsvnhelpers.utils import svn_branch


class TestUtils(BaseTestCase):

    def test_utils(self):
        os.chdir(self.clonedir)
        self.failUnless(is_svn())
        self.failIf(is_git())
        self.failUnlessEqual(svn_type(), 'trunk')
        self.failUnlessEqual(basename(), 'testrepo.svn')
        self.failUnlessEqual(svn_branch(), 'trunk')
