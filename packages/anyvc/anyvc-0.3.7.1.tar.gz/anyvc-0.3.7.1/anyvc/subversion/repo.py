"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import sys

import subvertpy
from subvertpy import repos, delta
from subvertpy.ra import RemoteAccess, Auth, get_username_provider, SubversionException
from anyvc.common.repository import Repository, Revision, join
from anyvc.common.commit_builder import CommitBuilder
from subvertpy.properties import time_from_cstring, time_to_cstring
from StringIO import StringIO


from datetime import datetime


class SubversionRevision(Revision):
    def __init__(self, repo, id):
        #XXX: branch subdirs
         self.repo, self.id = repo, id

    @property
    def parents(self):
        #XXX: ignore irelevant revisions (no local change)
        #XXX: use mergeinfo to figure additional parents
        if self.id == 1: # rev 0 is the repo creation
            return []
        return [SubversionRevision(self.repo, self.id -1)]

    def file_content(self, path):
        try:
            target = StringIO()
            self.repo.ra.get_file(path.lstrip('/'), target, self.id)
            return target.getvalue()
        except: #XXX: bad bad
            raise IOError('%r not found'%path)


    def path_info(self, path):
        return self.repo.ra.check_path(path, self.id)

    def exists(self, path):
        kind = self.path_info(path.lstrip('/'))
        return kind in (subvertpy.NODE_FILE, subvertpy.NODE_DIR)

    def prop(self, name):
        return self.repo.ra.rev_proplist(self.id).get(name)

    @property
    def message(self):
        return self.prop('svn:log')

    def get_changed_files(self):
        files = []
        def callback(paths, rev, props, childs=None):
            #XXX: take branch path into account?
            files.extend(paths)
        self.repo.ra.get_log(
            start = self.id,
            end = self.id,
            callback = callback,
            paths = None,
            discover_changed_paths=True)
        return files

    @property
    def author(self):
        return self.prop('svn:author')

    @property
    def time(self):
        date_str = self.prop('svn:date')
        timestamp = time_from_cstring(date_str)
        #XXX: subertpy uses a magic factor of 1000000
        return datetime.fromtimestamp(float(timestamp)/1000000)


class SvnCommitBuilder(CommitBuilder):
    def commit(self):
        ra = RemoteAccess(self.repo.url,
                          auth=Auth([get_username_provider()]))
        editor = ra.get_commit_editor({
            'svn:log':self.extra['message'],

            #XXX: subertpy uses a magic factor of 1000000
            #XXX: subversion cant set a commit date on commit, sucker
            #'svn:date':time_to_cstring(self.time_unix*1000000),
            })

        root = editor.open_root()

        for src, target in self.renames:
            #XXX: directories
            src = src.lstrip('/')
            target = target.lstrip('/')
            file = root.add_file(target, join(self.repo.url, src), 1)
            file.close()
            root.delete_entry(src)

        for file in self.contents:
            try:
                svnfile = root.add_file(file)
            except Exception as e:
                svnfile = root.open_file(file)
            txhandler = svnfile.apply_textdelta()
            f = StringIO(self.contents[file])
            delta.send_stream(f, txhandler)
            svnfile.close()
        root.close()
        editor.close()


class SubversionRepository(Repository):

    CommitBuilder = SvnCommitBuilder

    def __init__(self, path, create=False):
        #XXX: correct paths
        if create:
            repos.create(path.strpath)
        self.path = path
        self.url = "file://%s" % path
        self.ra = RemoteAccess(self.url)

    def __len__(self):
        return self.ra.get_latest_revnum()

    def get_default_head(self):
        #XXX: correct paths !!!, grab trunk
        last = len(self)
        if last == 0:
            return
        return SubversionRevision(self, last)

    def __getitem__(self, id):
        return SubversionRevision(self, id)

