# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    anyvc.mercurial
    ~~~~~~~~~~~~~~~

    Mercurial support

    :license: LGPL2 or later
    :copyright: 2008 Ronny Pfannschmidt
"""
import os
from functools import wraps

from anyvc.common.workdir import WorkDir, StatedPath
from ..exc import NotFoundError

try:
    import mercurial.util
    hgversion = mercurial.util.version()
    from mercurial.__version__ import version as hgversion
    if hgversion < '1.3':
        raise ImportError('HG version too old, please update to a release >= 1.3')
except AttributeError:
    raise ImportError('HG version too old, please update to a release >= 1.3')

from mercurial import ui as hgui, hg, commands, util, cmdutil
from mercurial.match import match, always
try:
    remoteui = cmdutil.remoteui
except AttributeError:
    remoteui = hg.remoteui

__all__ = 'Mercurial',



#XXX: this shouldn't work if used by the vc client
#     console output should be responsive
def grab_output(func):
    """
    wraps a call to hg and grabs the output
    """
    @wraps(func)
    def grabber(self, *k, **kw):
        self.repo.ui.pushbuffer()
        try:
            func(self, *k, **kw)
            return self.repo.ui.popbuffer()
        except Exception, e:
            e.hg_output = self.repo.ui.popbuffer()
            raise

    return grabber


class Mercurial(WorkDir):

    @property
    def repository(self):
        from .repo import MercurialRepository
        return MercurialRepository(workdir=self)

    def __init__(self, path, create=False, source=None):
        """
        Get a repo for a given path.
        If `create` is true, a new repo is created.
        """
        try:
            self.ui = hgui.ui(interactive=False, verbose=True, debug=True)
        except TypeError: # hg >= 1.3 ui
            self.ui = hgui.ui()
            self.ui.setconfig('ui', 'interactive', 'off')

        super(Mercurial, self).__init__(path, create, source)
        self.repo = hg.repository(self.ui, path.strpath)
        self.ui = self.repo.ui

    def create(self):
        hg.repository(self.ui, self.path.strpath, create=True)

    def setup(self):
        pass #XXX unneded

    def create_from(self, source):
        if hasattr(hg, 'peer'):
            hg.clone(remoteui(self.ui, {}), {},
                    str(source), self.path.strpath)
        else:
            hg.clone(remoteui(self.ui, {}),
                    str(source), self.path.strpath)

    def status(self, paths=(), *k, **kw):
        glob = '**' if kw.get('recursive') else '*'
        #XXX: merce conflicts ?!
        names = (
                'modified', 'added', 'removed',
                'missing', 'unknown', 'ignored', 'clean',
                )

        if paths:
        #XXX: investigate cwd arg
            matcher = match(self.repo.root, self.repo.root, paths,
                    default='relpath')
        else:
            matcher = always(self.repo.root, self.repo.root)

        state_files = self.repo.status(
            match=matcher,
            ignored=True,
            unknown=True,
            clean=True,
        )
        for state, files in zip(names, state_files):
            for file in files:
                yield StatedPath(file, state, base=self.path)



    @grab_output
    def add(self, paths=()):
        commands.add(self.ui, self.repo, *self.joined(paths))

    def joined(self, paths):
        if paths is None:
            return []
        return [os.path.join(self.repo.root, path) for path in paths]

    @grab_output
    def commit(self, paths=(), message=None, user=None):
        commands.commit(self.ui, self.repo,
            user=user,
            message=message,
            logfile=None,
            date=None,

            *self.joined(paths)
            )

    @grab_output
    def remove(self, paths):
        #XXX: support for after ?
        commands.remove(self.ui, self.repo,
                after=False, # only hg 0.9.5 needs that explicit
                force=False,
                *self.joined(paths)
                )

    @grab_output
    def revert(self, paths, rev=None): #XXX: how to pass opts['all']?
        if rev is None:
            parents = self.repo.parents()
            if len(parents)!=1 and rev is None:
                #XXX: better exception type?
                raise Exception(
                        "can't revert on top of a merge without explicit rev")
            rev = parents[0].rev()
        commands.revert(self.ui, self.repo,
                date=None,
                rev=rev,
                no_backup=False,
                *self.joined(paths))

    @grab_output
    def rename(self, source, target):
        commands.rename(self.ui, self.repo,
                after=False, # hg 0.9.5
                *self.joined([source, target])
                )

    @grab_output
    def diff(self, paths=(), rev=None):
        commands.diff(
                self.ui,
                self.repo,
                rev=rev,
                git=True,
                *self.joined(paths))


    @grab_output
    def update(self, paths=None, revision=None):
        assert paths is None
        commands.update(self.ui, self.repo, rev=revision)


