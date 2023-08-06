"""
    Anyvc Mercurial repository support
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>
"""

from anyvc.common.repository import Repository, Revision, join
from anyvc.common.commit_builder import CommitBuilder
from .workdir import grab_output
from datetime import datetime
from mercurial import commands, localrepo, ui, context
from mercurial import error, encoding
from ..exc import NotFoundError


class MercurialRevision(Revision):
    def __init__(self, repo, rev):
        self.repo, self.rev = repo, rev
    
    @property
    def id(self):
        return self.rev.hex()

    @property
    def author(self):
        return encoding.fromlocal(self.rev.user())

    @property
    def time(self):
        return datetime.fromtimestamp(self.rev.date()[0])

    @property
    def parents(self):
        return [MercurialRevision(self.repo, rev) for rev in self.rev.parents() if rev]


    @property
    def message(self):
        return encoding.fromlocal(self.rev.description())

    def file_content(self, path):
        try:
            return self.rev[path].data()
        except LookupError:
            raise IOError('%r not found'%path)

    def get_changed_files(self):
        return self.rev.files()

    def isdir(self, path):
        entries = list(self.rev)
        if not path.endswith('/'):
            path+='/'

        from bisect import bisect_right
        point = bisect_right(entries, path)
        if point >= len(entries):
            return False
        entry = entries[point]
        return path!=entry and entry.startswith(path)

    def isfile(self, path):
        return path in self.rev

    def exists(self, path):
        return self.isfile(path) or self.isdir(path)

class MercurialCommitBuilder(CommitBuilder):
    def commit(self):
        repo = self.repo.repo
        def get_file(repo, ctx, path):
            #XXX: copy sources
            #XXX: renames
            #XXX: deletes
            if path in rn and path not in self.contents:
                raise IOError()
            if path in rrn:
                assert base is not None
                parent = self.base_commit.rev[rrn[path]]
                if path in self.contents:
                    data = self.contents[path]
                else:
                    data = parent.data()
                copyed = rrn[path]
            else:
                data = self.contents[path]
                copyed = False

            islink = False #XXX
            isexec = False #XXX


            return context.memfilectx(path, data, islink, isexec, copyed)

        rn = dict((k, v) for k, v in self.renames if self.base_commit.exists(k))
        rrn = dict(reversed(x) for x in self.renames)
        #XXX: directory renames

        files = set(self.contents)
        files.update(rn.keys())
        files.update(rn.values())

        if self.base_commit is not None:
            base = self.base_commit.rev.node()
        else:
            base = None
        ctx = context.memctx(
                repo,
                [base, None],
                self.extra['message'],
                sorted(files),
                get_file,
                user=self.author,
                date="%(time_unix)d %(time_offset)s"%self.__dict__,
                )
        repo.commitctx(ctx)


class MercurialRepository(Repository):
    CommitBuilder = MercurialCommitBuilder

    def __init__(self, path=None, workdir=None, create=False):
        self.path = path
        self.workdir = workdir
        #XXX: path only handling
        if workdir is not None:
            self.repo = workdir.repo
            self.ui = self.repo.ui

        elif path is not None:
            try:
                repo = localrepo.localrepository(ui.ui(), str(path), create=create)
            except error.RepoError:
                raise NotFoundError('mercurial', path)

            self.ui = repo.ui
            self.repo = repo

    def invalidate_cache(self):
        self.repo.invalidate()

    @grab_output
    def push(self, dest=None, rev=None):
        self.invalidate_cache()
        commands.push(self.ui, self.repo, dest, rev=rev)

    @grab_output
    def pull(self, source="default", rev=None):
        self.invalidate_cache()
        commands.pull(self.ui, self.repo, source, rev=rev)

    def __len__(self):
        return len(self.repo)

    def get_default_head(self):
        return self['tip']

    def __getitem__(self, id):
        self.invalidate_cache()
        return MercurialRevision(self, self.repo[id])
