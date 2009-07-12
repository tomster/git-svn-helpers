import logging
import optparse
import sys
import os
from os.path import exists
from os.path import abspath
from glob import glob
from tee import popen
from config import GIT_CACHE
from utils import basename
from utils import is_svn
from utils import svn_log
from utils import base_url

logger = logging.getLogger("gitify")


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


class Command(object):

    def __init__(self, gitify):
        self.gitify = gitify


class CmdFetch(Command):

    def __init__(self, gitify):
        Command.__init__(self, gitify)
        self.parser = optparse.OptionParser(
            usage = "%prog fetch [<package-wildcard>]",
            description = """
Performs a git-svn fetch operation for the given packages inside the
cache directory. If no parameter is passed, all cached packages are
updated.
            """,
            add_help_option=False)
        self.parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true", default=False,
            help="""Show svn output.""")

    def __call__(self):
        options, args = self.parser.parse_args(sys.argv[2:])

        try:
            input = args[0]
        except IndexError:
            input = '*'

        cwd = os.getcwd()
        updated = 0
        for package in glob(abspath("%s/%s" % (GIT_CACHE, input))):
            os.chdir(package)
            print "fetching %s" % package
            popen("git svn fetch", options.verbose, True)
            updated += 1

        if updated > 0:
            print "Done. %d packages updated." % updated
        else:
            print "No packages found for %s" % input
        os.chdir(cwd)


class CmdPush(Command):

    def __init__(self, gitify):
        Command.__init__(self, gitify)
        self.parser = optparse.OptionParser(
            usage = "%prog push",
            description = """
Performs a dcommit with an ensuing svn update, to keep git and svn
in sync.
            """,
            add_help_option=False)
        self.parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true", default=False,
            help="""Show git-svn output.""")

    def __call__(self):
        options, args = self.parser.parse_args(sys.argv[2:])
        status, dummy = popen('git svn dcommit', options.verbose, True)
        if status == 0:
            popen('svn up --force', options.verbose, True)
            logger.info("Pushed local changes to svn.")
        else:
            logger.error("An error occurred, consult output above.")