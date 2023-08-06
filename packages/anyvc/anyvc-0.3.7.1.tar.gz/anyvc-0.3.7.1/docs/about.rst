==================
About
==================


`Anyvc` is a library to abstract common vcs operations.
It was born in an effort to enhance vcs operations in PIDA_.

The current version is mainly tailored to working with
the working directories of the different vcs's and
performing operations like adding/renaming/moving files,
showing differences to the current commit and creating new commits.

It's still in the early stages of development,
but has already proved its practical value
in the version control service of PIDA_.

Future versions will gradually expand the scope
from just workdir to interacting with history
as well as managing repositories and branches.

Due to the differences in the vcs's
not all operations are available on all vcs's,
the abstraction will degrade/warn/error in those cases.

.. _PIDA: http://pida.co.uk
