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

def svn_info():
    """Returns the svn info as XML element"""
    code, result = popen('svn info --xml .', False, False)
    return ElementTree.fromstring(''.join(result))

def svn_log():
    """Returns the svn log as XML element"""
    code, result = popen('svn log --stop-on-copy --xml .', False, False)
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
