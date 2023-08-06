VCS Abstraction Backends
=========================


Currently anyvc ships with support for


.. tableofcontents::


Mercurial
---------

The Mercurial backend is implemented in Terms of the basic Merucrial api.
It does not support extension discovery or extensions.


Git
----

The Git backend is split.
Workdir support is implemented in terms of the git CLI because Dulwich has no complete support.
Workdirs are still agnostic to the existence of the git index.
Repository support is implemented in terms of Dulwich, cause its supported and the better 'api'.


Subversion
-----------

The Subversion backend is split as well.
The workdir part is implemented in terms of the CLI,
because the Subversion checkout api requires complicated locking patterns.
The Repository support is implemented in terms of subvertpy.

