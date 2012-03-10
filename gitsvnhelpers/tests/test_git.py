import os
from jarn.mkrelease.tee import popen
from gitsvnhelpers.utils import is_git
from gitsvnhelpers.utils import is_svn
from gitsvnhelpers.utils import index_is_dirty
from gitsvnhelpers.utils import local_changes
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
        popen('git commit -m "added bar"', False, False)
        self.failIf(index_is_dirty())

    def test_local_changes(self):
        # A fresh repository doesn't have uncommitted changes:
        self.failIf(local_changes())
        # Adding a new file on the filesustem...
        newfile = open("%s/bar.txt" % self.packagedir, 'aw')
        newfile.write('This is bar\n')
        newfile.close()
        # ... changes that
        self.failUnless(local_changes())
        # Once we've actually committed the change, we're clean again:
        popen('git add bar.txt')
        self.failUnless(local_changes())
        popen('git commit -m "added bar"', False, False)
        self.failIf(local_changes())
        # Modifying an existing file will have the same effect:
        popen('echo "modified" >> bar.txt')
        self.failUnless(local_changes())
        popen('git add bar.txt')
        popen('git commit -m "modified bar"', False, False)
        self.failIf(local_changes())
