*****************************************
ZC Buildout recipe for Redhat RC scripts
*****************************************

This package provides a zc.buildout recipe for creating Red-Hat Linux
compatible run-control scripts.

.. contents::

Changes
*******

1.4.0 (2012-05-18)
==================

- Added optional process-management support.  If requested, then run
  scripts are run as part of install and uninstall.

- Fixed: missing dependency on ``zope.testing``

1.3.0 (2010/05/26)
==================

New Features
------------

- A new independent-processes option causes multiple processes to be
  restarted independently, rather then stoping all of the and the
  starting all of them.

Bugs Fixed
----------

- Generated run scripts had trailing whitespace.

1.2.0 (2009/04/06)
==================

displays the name of the script being run
for each script when it is started, stopped, or restarted

1.1.0 (2008/02/01)
==================

Use the deployment name option (as provided by zc.recipe.deployment
0.6.0 and later) if present when generating script names.

Use the deployment rc-directory as the destination when a deployment
is used.

Use /sbin/chkconfig rather than chkconfig, as I'm told it is always in
that location and rarely in anyone's path. :)

1.0.0 (2008/01/15)
==================

Initial public release
