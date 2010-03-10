git-svn-helpers is a collection of command line tools that greatly simplify
using git for svn repositories.

Its main goal is to make setting up a local git repository following an
existing svn checkout a 'no-brainer'.

It also addresses using a single git-svn repository for working on multiple
checkouts of (usually) different branches and switching between them.

Basic usage
===========

Executive summary::

    > cd path/to/svn/repo
    > gitify init

Perform local changes and commit them to git. When ready to push your changes::

    > gitify push

To update your working directory with upstream changes::

    > gitify update

gitify will take care to keep your git and svn repository in sync and do its best to avoid conflicts when updating.

Sample session
==============

Here's a sample session::

    > cd /tmp
    > svn co https://svn.plone.org/svn/plone/plone.app.form/branches/1.1 plone.app.form
    A    1.1/setup.py
    ...
    Checked out revision 27228.
    > cd plone.app.form
    > gitify init
    No git repository found in /Users/tomster/.gitcache/.
    Initiating cloning into cache.
    Analyzing svn log...
    Cloning https://svn.plone.org/svn/plone/plone.app.form/ from r10593:34543 into /Users/tomster/.gitcache/
    Initialized empty Git repository in /Users/tomster/Development/gitcache/plone.app.form/.git/
    ...
    Git branch 'local/1.1' is now following svn branch '1.1':
    # On branch local/1.1
    nothing to commit (working directory clean)
    > git branch
    * local/1.1
      master

Points to note:

 * gitify limited the cloning to the revisions found in the svn log of the package root (here ``https://svn.plone.org/svn/plone/plone.app.form/``). A big time saver, especially on large repositories (such as plone.collective)
 * gitify created a local branch ``local/1.1`` that follows the (remote) svn branch ``1.1`` and switched to it
 * gitify assumed that the name of the package is the name of the directory it 
   was called from (in this case ``plone.app.form``) as it refuses to guess

Multiple check-outs of the same package
=======================================

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
    > gitify init
    Updating existing cache:
    fetching /Users/tomster/.gitcache/plone.app.form
    Done. 1 packages updated.
    Git branch 'local/trunk' is now following svn branch 'trunk':
    # On branch local/trunk
    nothing to commit (working directory clean)

Notice, that this operation went much faster, as we now have used the existing git repository in the cache directory, thus avoiding the slow and network intensive clone operation.

This can be further evidenced by looking at the available local branches now. Notice how the git repository contains both trunk and the 1.1 branch::

    > git branch
      local/1.1
    * local/trunk
      master


Keeping the cache up-to-date
============================

Of course, once you introduce a cache you need to keep it up-to-date. ``git-svn``
provides the ``fetch`` command for this purpose. In practice it is cumbersome
to update each package manually, though. Therefore we provide our own ``fetch``
command which can update multiple packages at once using wildcards, like so::

    > gitify fetch plone*
    fetching /Users/tomster/.gitcache/plone.app.form
    fetching /Users/tomster/.gitcache/plone.pony
    fetching /Users/tomster/.gitcache/plonenext
    Done. 3 packages updated.

You can pass the ``-v`` option to see the output of the ``git-svn fetch`` commands.
If you don't provide a package *all* packages will be updated. 

Note, that the our fetch command never touches any working copy, only the cache. 
Is primarily intended to be run as a maintenance command, i.e. via crontab to keep
the local cache 'fresh'.


Keeping git and svn in sync
===========================

Since the local filesystem is both a git repository, as well as a svn check-
out *at the same time* (IOW we have both ``.git`` and ``.svn`` floating
around) they should be kept in sync as closely as possible. By design, this
can only happen, when we have online access to the svn repository. Therefore
it is best performed when committing back to svn. The way this is achieved
manually is to first dcommit and then perform a ``svn up --force`` command
(the ``--force`` is necessary so that svn won't be bothered by any new files
that have been committed). ``gitify push`` provides a convenience command that
performs this for you::

    > gitify push -v
    Committing to https://svn.plone.org/svn/plone/plone.app.form/branches/1.1 ...
    At revision 27229.
    INFO: Pushed local changes to svn.
    > svn st
    <BLANKLINE>

Installation
============

Simply use `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_,
optionally with `virtualenv <http://pypi.python.org/pypi/virtualenv>`_::

    > easy_install git-svn-helpers

Requirements
============

``git-svn-helpers`` requires that git (with subversion support a.k.a
``git-svn``) is already installed.


TODO
====

 * add support for custom svn layout
