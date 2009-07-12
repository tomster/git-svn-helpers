import logging
import optparse
import sys
import os
from os.path import exists

from config import GIT_CACHE
from tee import popen
from utils import basename
from utils import is_git
from utils import is_svn
from utils import svn_type
from utils import svn_branch
from utils import clone
from commands import Command
from commands import CmdPush
from commands import CmdFetch

logger = logging.getLogger("gitify")


class CmdGitify(Command):

    def __init__(self, gitify):
        Command.__init__(self, gitify)
        self.parser = optparse.OptionParser(
            usage = "%prog",
            description = """
            """,
            add_help_option=False)
        self.parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true", default=False,
            help="""Show git-svn output.""")

    def __call__(self):
        options, args = self.parser.parse_args(sys.argv[2:])

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
            popen('git checkout -f %s' % local_branch, False, False)
        else:
            popen('git checkout -f -b %s %s' % (local_branch, remote_branch),
                False, False)

        os.chdir(cwd)
        if not exists('.git'):
            popen('ln -s %s%s/.git' % (GIT_CACHE, package_name), False, False)

        print "Git branch '%s' is now following svn branch '%s':" % (
            local_branch, remote_branch)
        popen('svn status')
        popen('git status')


class CmdHelp(Command):

    def __init__(self, gitify):
        Command.__init__(self, gitify)
        self.parser = optparse.OptionParser(
            usage="%prog help [<command>]",
            description="Show help on the given command or about the whole "
                "script if none given.",
            add_help_option=False)

    def __call__(self):
        gitify = self.gitify
        if len(sys.argv) != 3 or sys.argv[2] not in gitify.commands:
            print("usage: %s <command> [options] [args]"
                % os.path.basename(sys.argv[0]))
            print("\nType '%s help <command>' for help on a specific command."
                % os.path.basename(sys.argv[0]))
            print("\nAvailable commands:")
            f_to_name = {}
            for name, f in gitify.commands.iteritems():
                f_to_name.setdefault(f, []).append(name)
            for cmd in sorted(x for x in dir(gitify) if x.startswith('cmd_')):
                name = cmd[4:]
                if name == 'pony':
                    continue
                f = getattr(gitify, cmd)
                aliases = [x for x in f_to_name[f] if x != name]
                if len(aliases):
                    print("    %s (%s)" % (name, ", ".join(aliases)))
                else:
                    print("    %s" % name)
        else:
            print gitify.commands[sys.argv[2]].parser.format_help()


class Gitify(object):

    def __call__(self, **kwargs):
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)

        if len(kwargs) == 0:
            if is_git():
                logger.error("This seems to be a local git repository!")
                return

            if not is_svn():
                logger.error("This only works on svn checkouts!")
                return

        self.cmd_push = CmdPush(self)
        self.cmd_fetch = CmdFetch(self)
        self.cmd_gitify = CmdGitify(self)
        self.cmd_help = CmdHelp(self)

        self.commands = dict(
            help=self.cmd_help,
            h=self.cmd_help,
            up = self.cmd_fetch,
            fetch = self.cmd_fetch,
            push = self.cmd_push,
            gitify = self.cmd_gitify,
        )

        try:
            command = sys.argv[1]
        except IndexError:
            command = 'gitify'

        self.commands.get(command, self.unknown)()

    def unknown(self):
        logger.error("Unknown command '%s'." % sys.argv[1])
        logger.info("Type '%s help' for usage." % \
            os.path.basename(sys.argv[0]))
        sys.exit(1)


gitify = Gitify()
