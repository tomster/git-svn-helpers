import optparse
import os
from os.path import abspath
from glob import glob
from jarn.mkrelease.tee import popen
import config
from utils import local_changes

class Command(object):

    def __init__(self, gitify):
        self.gitify = gitify


class CmdFetch(Command):

    def __init__(self, gitify, args=None):
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
        options, args = self.parser.parse_args(self.gitify.args[2:])

        try:
            input = args[0]
        except IndexError:
            input = '*'

        cwd = os.getcwd()
        updated = 0
        for package in glob(abspath("%s/%s" % (config.GIT_CACHE, input))):
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

    def __call__(self):
        options, args = self.parser.parse_args(self.gitify.args[2:])
        status, dummy = popen('git svn dcommit', True, True)
        if status == 0:
            popen('svn up --force', True, True)
            print "Pushed local changes to svn."
        else:
            print "An error occurred, consult output above."


class CmdUpdate(Command):

    def __init__(self, gitify, args=None):
        Command.__init__(self, gitify)
        self.parser = optparse.OptionParser(
            usage = "%prog update",
            description = """
Performs a git-svn rebase operation for the current svn checkout.
            """,
            add_help_option=False)

    def __call__(self):
        options, args = self.parser.parse_args(self.gitify.args[2:])
        stashed = False
        if local_changes():
            stashed = True
            print "Stashing uncommitted local changes."
            status, dummy = popen('git stash', False, False)
        status, dummy = popen('git svn rebase', False, False)
        for line in dummy:
            print line
        if stashed:
            status, dummy = popen('git stash pop', False, False)
