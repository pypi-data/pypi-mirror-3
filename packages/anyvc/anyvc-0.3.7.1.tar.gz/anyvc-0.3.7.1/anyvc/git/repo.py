"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""


from anyvc.common.repository import Repository, Revision
from anyvc.common.commit_builder import CommitBuilder
from ..exc import NotFoundError
import subprocess
import stat
import os
from py.path import local
from datetime import datetime
from collections import defaultdict
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from dulwich.errors import NotGitRepository

class GitRevision(Revision):

    def __init__(self, repo, commit):
        self.repo, self.commit = repo, commit

    @property
    def id(self):
        return self.commit.id

    @property
    def author(self):
        return self.commit.author

    @property
    def time(self):
        #XXX distinct author and commiters?
        return datetime.fromtimestamp(self.commit.author_time)

    @property
    def parents(self):
        return [GitRevision(self.repo, self.repo.repo[id])
                for id in self.commit.parents]

    @property
    def message(self):
        return self.commit.message.rstrip()


    def resolve(self, path):
        repo = self.repo.repo
        tree = repo.get_object(self.commit.tree)
        result = tree.lookup_path(repo.get_object, path)
        return repo[result[1]]

    def file_content(self, path):
        try:
            #XXX: highly incorrect, should walk and check the type
            blob = self.resolve(path)
            assert blob.__class__ is Blob
            return blob.data
        except KeyError:
            raise IOError('%r not found'%path)

    def exists(self, path):
        try:
            self.resolve(path)
            return True
        except KeyError:
            return False

    def isfile(self, path):
        try:
            return self.resolve(path).__class__ is Blob
        except KeyError:
            return False

    def get_changed_files(self):
        new = self.commit.tree
        if self.parents:
            old = self.parents[0].commit.tree
        else:
            old = None
        #XXX: bad code
        added, removed, changed = diff_tree(self.repo.repo, old, new)
        return sorted(added | removed | changed)

class GitCommitBuilder(CommitBuilder):

    def commit(self):
        #XXX: evidence for the rest of 
        # this functions is supposed not to exist
        # yes, its that 

        #XXX: generate all objects at once and 
        #     add them as pack instead of legacy objects

        r = self.repo.repo
        store = r.object_store
        new_objects = []
        names = sorted(self.contents)
        nametree = defaultdict(list)
        for name in names:
            base = name.strip('/')
            while base:
                nbase = os.path.dirname(base)
                nametree[nbase].append(base)
                base = nbase

        if self.base_commit:
            tree = r.tree(self.base_commit.commit.tree)
            tree._ensure_parsed()
            print tree._entries
        else:
            tree = Tree()

        for src, dest in self.renames:
            src = src.strip('/')
            dest = dest.strip('/')
            tree[dest] = tree[src]
            del tree[src]


        for name in names:
            blob = Blob()
            blob.data = self.contents[name]
            new_objects.append((blob, name))
            tree.add(0555, os.path.basename(name), blob.id)
        new_objects.append((tree, ''))
        commit = Commit()
        if self.base_commit:
            commit.parents = [self.base_commit.commit.id]
        commit.tree = tree.id
        commit.message = self.extra['message']
        commit.committer = self.author
        commit.commit_time = int(self.time_unix)
        commit.commit_timezone = self.time_offset
        commit.author = self.author
        commit.author_time = int(self.time_unix)
        commit.author_timezone = self.time_offset
        new_objects.append((commit, ''))
        store.add_objects(new_objects)
        self.repo.repo.refs['HEAD'] = commit.id

class GitRepository(Repository):
    CommitBuilder = GitCommitBuilder

    def __init__(self, path=None, workdir=None, create=False, bare=False):
        assert path or workdir
        if workdir:
            self.path = workdir.path
        else:
            self.path = path
        if create:
            #XXX: fragile
            path.ensure(dir=1)
            self.repo = Repo.init(path.strpath)
        else:
            assert self.path.check(dir=True)
            try:
                self.repo = Repo(self.path.strpath)
            except NotGitRepository:
                raise NotFoundError('git', self.path)

    def __len__(self):
        #XXX: fragile
        head = self.get_default_head()
        if head is None:
            return 0
        return len(self.repo.revision_history(head.id))

    def push(self):
        #XXX: hell, figure if the remote is empty, push master in that case
        #XXX: use dulwich?
        subprocess.check_call(['git', 'push', '--all'], cwd=self.path)

    def get_default_head(self):
        revs = self.repo.get_refs()
        head = revs.get('HEAD', revs.get('master'))
        if head is not None:
            return GitRevision(self, self.repo.get_object(head))

    def __getitem__(self, id):
        return GitRevision(self, self.repo.get_object(id))




def walk_tree_object(repo, tree, path=''):
    for mode, name, sha in tree.entries():
        if stat.S_IFDIR & mode:
            for name, sha in walk_tree(repo, sha, name):
                yield os.path.join(path, name), sha
        else:
            yield os.path.join(path, name), sha

def walk_tree(repo, tree_id, path=''):
    if tree_id is None:
        return ()
    tree = repo.get_object(tree_id)
    assert tree.__class__ is Tree
    return walk_tree_object(repo, tree, path)


def diff_tree(repo, old, new):
    #XXX: bad code
    new_sha = dict(walk_tree(repo, new))
    old_sha = dict(walk_tree(repo, old))
    new_set = set(new_sha)
    old_set = set(old_sha)

    added = new_set - old_set
    removed = old_set - new_set

    changed = set(name
            for name, sha in new_sha.items()
            if name not in added
            and name not in removed
            and old_sha[name] != sha)
    return added, removed, changed





