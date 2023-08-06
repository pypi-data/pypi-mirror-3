# copyright 2008 by Ronny Pfannschmidt
# license lgpl3 or later

from __future__ import with_statement

from anyvc.metadata import state_descriptions

class WdWrap(object):
    """
    :param wd: the workdir to wrap
    :type wd: subclass of :class:`anyvc.common.workdir.Workdir`

    decorator for a vcs workdir instance
    adds testing utility functions and proxies the other methods/attributes
    to the real instance
    """
    def __init__(self, wd):
        self.__wd = wd

    def __getattr__(self, name):
        return getattr(self.__wd, name)


    def put_files(self, mapping):
        """
        :type mapping: dict of (filename, text content)

        the text content will be rstripped and get a newline appended
        """
        for name, content in mapping.items():
            path = self.path.ensure(name)
            path.write(content.rstrip() + '\n')

    def has_files(self, *files):
        """
        :arg files: a listing of filenames that shsould exist
        """
        missing = [name for name in map(self.path.join, files) if not name.check()]
        assert not missing, 'missing %s'%', '.join(missing)
        return not missing

    def delete_files(self, *relpaths):
        """
        :arg relpaths: listing of files to remove
        """
        for path in relpaths:
            self.path.join(path).remove()

    def check_states(self, exact=True, **kw):
        """
        .. better listing of the states!

        :param bool exact: if true, ignore additional states
        :keyword $statename: state name for that particular file list
        :type $statename: list of relative path
        :returns: True if all supplied files have the asumed state

        """
        __tracebackhide__ = True
        assert isinstance(exact, bool)
        mapping = dict((rn, state) for state, rns in kw.items() for rn in rns)
        print mapping
        used = set()
        all = set()
        infos = list(self.status())
        print infos
        for info in infos:
            all.add(info.abspath)
            print info
            assert info.state in state_descriptions
            if info.relpath in mapping:
                expected = mapping[info.relpath]
                assert info.state==expected, "%s wanted %s but got %s"%(
                        info.relpath,
                        expected,
                        info.state,
                        )
                used.add(info.relpath)

        untested = set(mapping) - used

        print 'all:', sorted(all)
        print 'used:', sorted(used)
        print 'missing?:', sorted(all - used)
        print 'untested:', sorted(untested)
        assert not untested , 'not all excepted stated occured'


class VcsMan(object):
    """
    utility class to manage the creation of repositories and workdirs
    inside of a specific path (usually the tmpdir funcarg of a test)
    """
    def __init__(self, vc, base, xspec, backend):
        self.remote = xspec is not None
        self.vc = vc
        self.base = base.ensure(dir=True)
        self.xspec = xspec
        self.backend = backend

    def __repr__(self): 
        return '<VcsMan %(vc)s %(base)r>'%vars(self)

    def create_wd(self, workdir, source=None):
        """
        :param workdir: name of the target workdir
        :type workdir: str
        :param source: name of a source repository
        :type source: repo or None

        create a workdir if `source` is given, use it as base
        """
        path = self.base/workdir
        source_path = getattr(source, 'path', None)
        wd = self.backend.Workdir(path, create=True, source=source_path)
        return WdWrap(wd)

    def make_repo(self, name):
        """
        :param name: name of the repository to create

        create a repository using the given name
        """
        return self.backend.Repository(path=self.base/name, create=True)

