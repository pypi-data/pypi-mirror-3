Workdir Api Examples
======================



Interactive Example Session
-----------------------------

Lets begin by setting up some essential basics::

  >>> from py.path import local
  >>> from anyvc import workdir
  >>> path = local('~/Projects/anyvc')
  >>> wd = workdir.open(path)


Now lets add a file::

  >>> path.join('new-file.txt').write('test')
  >>> wd.add(paths=['new-file.txt'])

Paths can be relative to the workdir, absolute paths,
or `py.path.local` instances.

Now lets take a look at the list of added files::

  >>> [s for s in wd.status() if s.state=='added']
  [<added 'new-file.txt'>]

Since we seem to be done lets commit::

  >>> wd.commit(
  ...     message='test',
  ...     paths=['new-file.txt'],
  ... )

Since the change is commited the list of added files is empty now::

  >>> [s for s in wd.status() if s.state=='added']
  []

