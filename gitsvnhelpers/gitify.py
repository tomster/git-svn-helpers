import sys
import os
from os.path import exists
from jarn.mkrelease.tee import popen

from config import GIT_CACHE
from utils import basename
from utils import is_git
from utils import is_svn
from utils import svn_type
from utils import svn_branch
from clone import clone


def main(args=None):

    if is_git():
        print "This seems to be a local git repository!"
        sys.exit(1)

    if not is_svn():
        print "This only works on svn checkouts!"
        sys.exit(1)

    package_name = basename()

    svntype = svn_type() 
    if svntype == 'tags':
        print "Can't work on tags!"
        sys.exit(1)
    elif svntype == 'unrecognized':
        print "Unrecognized svn structure!"
        sys.exit(1)

    if not exists(GIT_CACHE + package_name):
        print "No git repository found in %s." % GIT_CACHE
        print "Initiating cloning into cache."
        clone()
        fresh = True
    else:
        fresh = False

    # get the branch svn is on
    remote_branch = svn_branch()
    # the following is just convention:
    local_branch = "local/%s" % remote_branch

    cwd = os.getcwd()
    # perform all index updates in the cache to avoid conflicts
    os.chdir(GIT_CACHE + package_name)

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

    print "Git branch '%s' is now following svn branch '%s':" % (
        local_branch, remote_branch)
    popen('svn st')
    popen('git st')

    return 0


if __name__ == '__main__':
    sys.exit(main())
