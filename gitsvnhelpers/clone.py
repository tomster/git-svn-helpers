import sys
import os
from os.path import exists
from jarn.mkrelease.tee import popen
from config import GIT_CACHE
from utils import basename
from utils import is_svn
from utils import svn_log
from utils import svn_url
from utils import svn_type


def clone():

    """
    A convenience/efficiency wrapper around git-svn clone that tries to figure
    out the first and last revisions of the given package that need to be
    cloned and then just clones that range.

    This is particularly useful for large repositories such as plone and its
    collective.
    Original (bash) code from Andreas Zeidler a.k.a. witsch
    """

    if not is_svn():
        print "This only works on svn checkouts!"
        sys.exit(1)

    package_name = basename()

    if exists(GIT_CACHE + package_name):
        print "git repository already found in %s%s." % (GIT_CACHE,
            package_name)
        sys.exit(1)
    print "Analyzing svn log..."
    logentries = svn_log().getiterator('logentry')
    last_revision = logentries[0].attrib['revision']
    first_revision = logentries[-1].attrib['revision']
    svntype = svn_type()
    svnurl = svn_url()
    base_url = svnurl.split(svntype)[0]

    print "Cloning %s from r%s:%s into %s" % (
        base_url, first_revision, last_revision, GIT_CACHE
    )
    
    cwd = os.getcwd()
    if not exists(GIT_CACHE):
        os.mkdir(GIT_CACHE)
    os.chdir(GIT_CACHE)
    popen("git svn clone -r%s:%s %s -s" % (first_revision,
        last_revision, base_url))

    os.chdir(cwd)
    return 0


if __name__ == '__main__':
    sys.exit(clone())
