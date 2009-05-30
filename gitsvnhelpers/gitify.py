import sys
import os
from os.path import exists
from jarn.mkrelease.tee import popen

from config import GIT_CACHE
from utils import basename
from utils import is_git
from utils import is_svn
from utils import svn_url
from utils import svn_branch


def main(args=None):

    if is_git():
        print "This seems to be a local git repository!"
        sys.exit(1)

    if not is_svn():
        print "This only works on svn checkouts!"
        sys.exit(1)

    package_name = basename()

    if not exists(GIT_CACHE + package_name):
        print "No git repository found in %s." % GIT_CACHE
        sys.exit(1)

    # get the branch svn is on
    if '/tags/' in svn_url():
        print "Can't work on tags!"
        sys.exit(1)

    remote_branch = svn_branch()
    # the following is just convention:
    local_branch = "local/%s" % remote_branch

    cwd = os.getcwd()
    # perform all index updates in the cache to avoid conflicts
    os.chdir(GIT_CACHE + package_name)
    popen('git fetch', False, False)

    dummy, existing_branches = popen('git b', False, False)
    existing_branches = [b.strip() for b in existing_branches]
    if local_branch in existing_branches:
        popen('git co -f %s' % local_branch, False, False)
    else:
        popen('git co -f -b %s %s' % (local_branch, remote_branch), False,
            False)

    os.chdir(cwd)
    if not exists('.git'):
        popen('ln -s %s%s/.git' % (GIT_CACHE, package_name), False, False)

    popen('git svn rebase', False, False)
    print "Git branch '%s' is now following svn branch '%s':" % (
        local_branch, remote_branch)
    popen('svn st')
    popen('git st')

    return 0


if __name__ == '__main__':
    sys.exit(main())
