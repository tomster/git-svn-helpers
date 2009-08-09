import os
from jarn.mkrelease.tee import popen
from gitsvnhelpers.utils import is_git
from gitsvnhelpers.utils import is_svn
from gitsvnhelpers.utils import index_is_dirty
from gitsvnhelpers.testing import GitTestCase


class TestGit(GitTestCase):

    def test_scm_type(self):
        # make sure it's not svn, but indeed a git repository:
        self.failIf(is_svn())
        self.failUnless(is_git())

    def test_dirty_index(self):
        # A fresh repository is never dirty:
        self.failIf(index_is_dirty())
        # Adding a new file on the filesustem...
        newfile = open("%s/bar.txt" % self.packagedir, 'aw')
        newfile.write('This is bar\n')
        newfile.close()
        # ... doesn't change that
        self.failIf(index_is_dirty())
        # only after adding it to the index will it become 'dirty'
        popen('git add bar.txt')
        self.failUnless(index_is_dirty())
        # Once we've actually committed the change, we're clean again:
        popen('git ci -m "added bar"', False, False)
        self.failIf(index_is_dirty())
