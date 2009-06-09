git-svn-helpers is a collection of command line tools that greatly simplify
using git for svn repositories.

Its main goal is to make setting up a local git repository following an
existing svn checkout a 'no-brainer'.

It also addresses using a single git-svn repository for working on multiple
checkouts of (usually) different branches and switching between them.

Basic usage (Example)
=====================

Executive summary::

    > cd path/to/svn/repo
    > gitify

Here's a sample session::

    > cd /tmp
    > svn co https://svn.plone.org/svn/plone/plone.app.form/branches/1.1 plone.app.form
    A    1.1/setup.py
    ...
    Checked out revision 27228.
    > cd plone.app.form
    > gitify
    No git repository found in /Users/tomster/.gitcache/.
    Initiating cloning into cache.
    Analyzing svn log...
    Cloning https://svn.plone.org/svn/plone/plone.app.form/ from r10593:27155 into /Users/tomster/.gitcache/
    Initialized empty Git repository in /Users/tomster/.gitcache/plone.app.form/.git/
    ...
    Git branch 'local/1.1' is now following svn branch '1.1':
    # On branch local/1.1
    nothing to commit (working directory clean)
    > git branch
    * local/1.1
      master

Points to note:

 * gitify limited the cloning to the revisions found in the svn log of the package root (here ``https://svn.plone.org/svn/plone/plone.app.form/``). A big time saver, especially on large repositories (such as plone.collective)
 * gitify created the git repository at ``~/.gitcache`` *not in place*
 * gitify created a local branch ``local/1.1`` that follows the (remote) svn branch ``1.1`` and switched to it

Multiple check-outs
===================

In practice you will often work with different local copies of a given repository, i.e. on trunk and on a feature branch. That's when the ``.gitcache`` directory created above comes in handy. Let's move our previous checkout out of the way and create a maintenance checkout that follows trunk::

    > cd ..
    > mkdir feature-branch
    > mv plone.app.form feature-branch/
    > mkdir maintenance
    > cd maintenance/
    > svn co https://svn.plone.org/svn/plone/plone.app.form/trunk plone.app.form
    A    plone.app.form/setup.py
    ...
     U   plone.app.form
    Checked out revision 27228.

What happens if we run gitify here?::

    > cd plone.app.form/
    > gitify
    Git branch 'local/trunk' is now following svn branch 'trunk':
    # On branch local/trunk
    nothing to commit (working directory clean)

Notice, that this operation went much faster, as we now have used the existing git repository in the cache directory. This can be further evidenced by looking at the available local branches now::

    > git branch
      local/1.1
    * local/trunk
      master

Caveats
=======

'Recycling' ``.git`` in this manner works (perhaps surprisingly) well in practice, but you need to keep the following in mind:

**All checkouts share the same index!**

Let's take a look at what this means by switching back to our feature branch::

    > cd ../../feature-branch/plone.app.form/
    > git status
    # On branch local/trunk
    # Changed but not updated:
    #   (use "git add/rm <file>..." to update what will be committed)
    #   (use "git checkout -- <file>..." to discard changes in working directory)
    #
    #	modified:   docs/HISTORY.txt
    ...
    #	deleted:    plone/app/form/kss/tests/test_kss.py
    ...
    #
    # Untracked files:
    #   (use "git add <file>..." to include in what will be committed)
    #
    #	plone/app/form/tests/test_kss.py

Wohah! What happened is that ``.git`` now points to trunk and thus the status
command shows the difference between that and our branch as local
modifications, since that is what the filesystem represents. We can verify
this by using subversions status command::

    > svn st
    <BLANKLINE>

Phew! All in order! But what to do with git? We've finished working on trunk
and want to get back to our feature branch, but the git index is all wrong?!
Simple: just re-run gitify::

    > gitify
    Git branch 'local/1.1' is now following svn branch '1.1':
    # On branch local/1.1
    nothing to commit (working directory clean)

Basically, that's all you need to remember when working with multiple
check-outs of the same package: **Always run gitify when switching between
check-outs!**

Keeping the cache up-to-date
============================

Of course, once you introduce a cache you need to keep it up-to-date. ``git-svn``
provides the ``fetch`` command for this purpose. In practice it is cumbersome
to update each package manually, though. Therefore we provide the ``gs-fetch``
command which can update multiple packages at once using wildcards, like so::

    > gs-fetch plone*
    fetching /Users/tomster/.gitcache/plone.app.form
    fetching /Users/tomster/.gitcache/plone.pony
    fetching /Users/tomster/.gitcache/plonenext
    Done. 3 packages updated.

You can pass the ``-v`` option to see the output of the ``git-svn fetch`` commands.
If you don't provide a package *all* packages will be updated. This is useful
for automated updates, i.e. from crontab.

Keeping git and svn in sync
===========================

Since the local filesystem is both a git repository, as well as a svn check-
out *at the same time* (IOW we have both ``.git`` and ``.svn`` floating
around) they should be kept in sync as closely as possible. By design, this
can only happen, when we have online access to the svn repository. Therefore
it is best performed when committing back to svn. The way this is achieved
manually is to first dcommit and then perform a ``svn up --force`` command. 
The ``--force`` is necessary so that svn won't be bothered by any new files
that have been committed::

    > gs-commit
    Committing to https://svn.plone.org/svn/plone/plone.app.form/branches/1.1 ...
    At revision 27229.
    > svn st
    <BLANKLINE>


TODO
====

'Recycling' git repositories with symlinks is sub-optimal. Ideally we would
want to create local clones (IOW replace the symlink command with a ``git
clone`` command). *However*, ``git clone`` currently doesn't preserve the svn
information of the source. That means we couldn't dcommit from our cloned
repository! Eventually, this should be fixed up-stream in git svn.
