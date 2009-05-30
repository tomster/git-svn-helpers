from os.path import exists, isdir, islink
from elementtree import ElementTree
from jarn.mkrelease.tee import popen

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

def svn_url():
    """ returns the URL of the svn checkout"""
    code, result = popen('svn info --xml .', False, False)
    svninfo = ElementTree.fromstring(''.join(result))
    return svninfo.find('entry/url').text

def svn_branch():
    """ returns the name of the branch that this svn checkout
        is on"""
    return svn_url().split('/')[-1]