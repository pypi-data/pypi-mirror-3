"""
    anyvc.remote
    ~~~~~~~~~~~~

    run packends in different processes and on different computers
    also circumvent the gpl


    :license: lgpl2
    :copyright: 2009 by Ronny Pfannschmidt

"""
from execnet import makegateway
from os.path import join

from anyvc.exc import NotFoundError
from anyvc.util import cachedproperty
from .object import RemoteCaller
from anyvc.common.commit_builder import CommitBuilder, FileBuilder, RevisionBuilderPath
from anyvc.common.repository import MemoryFile
from anyvc.metadata import backends
import time
import datetime
from py.path import local

class RemoteCommit(object):
    def __init__(self, repo, id):
        self.repo = repo
        self.id = id

    def get_parent_diff(self):
        return self.repo.commit_diff(self.id)

    def exists(self, path):
        return self.repo.commit_exists(self.id, path)

    def file_content(self, path):
        data = self.repo.commit_file_content(self.id, path)
        if data is None:
            raise IOError('%r not found'%path)
        return data

    @cachedproperty
    def parents(self):
        return [RemoteCommit(self.repo, id)
                for id in self.repo.commit_parents(self.id)]

    @cachedproperty
    def author(self):
        return self.repo.commit_author(self.id)

    @cachedproperty
    def message(self):
        return self.repo.commit_message(self.id)

    def __enter__(self):
        from anyvc.common.repository import RevisionView
        return RevisionView(self, '')

    @cachedproperty
    def time(self):
        return datetime.datetime.fromtimestamp(self.repo.commit_time(self.id))

    def __exit__(self, et, ev, tb):
        pass


class RemoteRepository(RemoteCaller):
    
    @cachedproperty
    def path(self):
        return local(self._call_remote('path'))

    def get_commit(self, id):
        return RemoteCommit(self, id)

    def get_default_head(self):
        id = self._call_remote('get_default_head')
        return self.get_commit(id)

    def transaction(self, *k, **kw):
        t = kw.get('time')
        if isinstance(t, datetime.datetime): #XXX: fragile
            t = time.mktime(t.timetuple())
            kw['time'] = t
        channel = self._call_remote('transaction', *k, **kw)
        return RemoteTransaction(channel)

    def __len__(self):
        return self._call_remote('count_revisions')


class RemoteWorkdir(RemoteCaller):

    def status(self, **kw):
        from anyvc.common.workdir import StatedPath
        items = self._call_remote('status', **kw)
        for path, base, state in items:
            yield StatedPath(path, state, base)

    @property
    def repository(self):
        #XXX: this one shouldnt be
        channel = self._call_remote('get_local_repo')
        if channel is not None:
            return RemoteRepository(channel)

    @cachedproperty
    def path(self):
        return local(self._call_remote('get_path'))


class RemoteTransaction(RemoteCaller):
    def __enter__(self):
        #XXX: take remote commit into account
        return RevisionBuilderPath(None, '', self)
    def __exit__(self, etype,  eval, tb):
        if etype is None:
            self.commit()


class RemoteBackend(object):
    def __init__(self, backend, module, spec):
        self.spec = spec
        self.name = backend
        self.module_name = module
        self.gateway = makegateway(spec)
        channel = self.gateway.remote_exec("""
            from anyvc.remote.slave import start_controller
            start_controller(channel)
        """)
        channel.send(backend)
        channel.send(module)
        self._channel = channel.receive()
        if self._channel is None:
            raise ImportError('module %s not found on remote' % module)
        self._caller = RemoteCaller(self._channel)
        self.active = True

    def stop(self):
        #XXX: propperly shutdown the slave?
        self._channel.close()
        self.gateway.exit()
        self.active = False

    @property
    def features(self):
        return self._caller.features()

    def is_repository(self, path):
        return self._caller.is_repository(path=path)

    def is_workdir(self, path):
        return self._caller.is_workdir(path=path)

    def Repository(self, **kw):
        newchan = self._caller.open_repo(**kw)
        return RemoteRepository(newchan)

    def Workdir(self, path, **kw):
        kw['path'] = str(path)
        if kw.get('source'): # might be none
            kw['source'] = str(kw['source'])
        newchan = self._caller.open_workdir(**kw)
        return RemoteWorkdir(newchan)
