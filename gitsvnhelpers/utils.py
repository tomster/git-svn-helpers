import sys
import os
from os.path import exists, isdir, islink
from elementtree import ElementTree
from jarn.mkrelease.tee import popen
from config import GIT_CACHE


def basename():
    return popen('basename $PWD', False, False)[1][0]


def is_git():
    """ Is the current directory a git local repository?
        (as opposed to no git repository at all or just a symlink)
    """
    return exists('.git') and not islink('.git')


def is_svn():
    """is the current directory a svn checkout?"""
    return (exists('.svn') and isdir('.svn'))


def svn_info():
    """Returns the svn info as XML element"""
    code, result = popen('svn info --xml .', False, False)
    return ElementTree.fromstring(''.join(result))


def svn_log():
    """Returns the svn log of the base url as XML element"""
    code, result = popen('svn log --stop-on-copy --xml %s' % base_url(),
        False, False)
    return ElementTree.fromstring(''.join(result))


def svn_url(svninfo=None):
    """ returns the URL of the svn checkout"""
    if svninfo is None:
        svninfo = svn_info()
    return svninfo.find('entry/url').text


def svn_branch():
    """ returns the name of the branch that this svn checkout
        is on"""
    return svn_url().split('/')[-1]


def base_url():
    return svn_url().split(svn_type())[0]


def svn_type():
    url = svn_url()
    if '/trunk' in url:
        return 'trunk'
    elif '/tags' in url:
        return 'tags'
    elif '/branches' in url:
        return 'branches'
    else:
        return 'unrecognized'

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
    baseurl = base_url()

    print "Cloning %s from r%s:%s into %s" % (
        baseurl, first_revision, last_revision, GIT_CACHE)

    cwd = os.getcwd()
    if not exists(GIT_CACHE):
        os.mkdir(GIT_CACHE)
    os.chdir(GIT_CACHE)
    popen("git svn clone -r%s:%s %s -s" % (first_revision,
        last_revision, baseurl))

    os.chdir(cwd)
    return 0

