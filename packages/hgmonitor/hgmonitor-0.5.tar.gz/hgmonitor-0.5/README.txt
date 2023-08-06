Introduction
------------

The monitor extension tracks a directory of hg repositories for changes which
are not committed or pushed to the server.  The basic use case is for easily
tracking a set of diverse repositories for pending changes.  Another use is to
schedule an e-mail updating on the state of pending changes.

All monitor commands take an optional directory argument and a boolean recurse
flag.  The default (recurse False) is to recurse one directory, but when recurse
is true, monitor searches for all hg repositories under the directory.

In addition, if the mq switch is enabled, then monitor searches for hg
repositories in .hg\patches inside each main repository found.

In some ways, this extension provides a much more flexible notion of
sub-repositories.  There is no tracking of related repositories beyond being in
the same sub-directory.  Such simplicity can allow a more flexible workflow.

Examples
--------

List changes in repositories directly under the current working directory::

    hg monitor

List changes in all repositories under the given directory or directories::

    hg monitor --dir=<dir1> --dir=<dir2> --recurse

Pull changes from the default repository for all repositories in the scope of
the command::

    hg mpull --update

::

    hg mpush

The mbackup command has facilities for backing up uncommitted changes 
(and unpushed changesets - in the future).  It could also be a 
directory::

    hg mbackup --dir=<directory> --remote=<additional backup folder>

Changelog
---------

* 0.5 - fixed bug with --dir selectors not accumulating when they point
  directly to repositories -- Thanks Piotr Owsiak

* 0.4 - added email from monitor and extended zipped backup to include 
  outgoing changes

* 0.3 - added mbackup with zip & copy for uncommitted changes

Future
------

The monitor command will include the ability to e-mail uncommitted/unpushed
changes to an e-mail address::

    hg monitor --dir=<directory> --email
