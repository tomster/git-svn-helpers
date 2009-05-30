import sys
import os
from os.path import exists, isdir, islink, expanduser
from jarn.mkrelease.tee import popen
from elementtree import ElementTree

GIT_CACHE = expanduser('~/.gitcache/')


def main(args=None):

    if exists('.git') and not islink('.git'):
        print "This seems to be a local git repository!"
        sys.exit(1)

    if not (exists('.svn') and isdir('.svn')):
        print "This only works on svn checkouts!"
        sys.exit(1)

    basename = popen('basename $PWD', False, False)[1][0]

    if not exists(GIT_CACHE + basename):
        print "No git repository found in %s." % GIT_CACHE
        sys.exit(1)

    # get the branch svn is on
    code, result = popen('svn info --xml .', False, False)
    svninfo = ElementTree.fromstring(''.join(result))
    svnurl = svninfo.find('entry/url').text.split('/')

    if svnurl[-2] == 'tags':
        print "Can't work on tags!"
        sys.exit(1)

    remote_branch = svnurl[-1]
    # the following is just convention:
    local_branch = "local/%s" % remote_branch

    cwd = os.getcwd()
    # perform all index updates in the cache to avoid conflicts
    os.chdir(GIT_CACHE + basename)
    popen('git fetch', False, False)

    dummy, existing_branches = popen('git b', False, False)
    existing_branches = [b.strip() for b in existing_branches]
    if local_branch in existing_branches:
        popen('git co -f %s' % local_branch, False, False)
    else:
        popen('git co -f -b %s %s' % (local_branch, remote_branch), False, False)

    os.chdir(cwd)
    if not exists('.git'):
        popen('ln -s %s%s/.git' % (GIT_CACHE, basename), False, False)

    popen('git svn rebase', False, False)
    print "Git branch '%s' is now following svn branch '%s':" % (
        local_branch, remote_branch)
    popen('svn st')
    popen('git st')

    return 0


if __name__ == '__main__':
    sys.exit(main())
