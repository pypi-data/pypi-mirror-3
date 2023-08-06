"""
    anyvc commit builder
    ~~~~~~~~~~~~~~~~~~~~

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt

    Base classes for building commits in memory
"""

from os.path import join, dirname
import time as unixtime
from datetime import datetime

from anyvc.common.repository import MemoryFile

class CommitBuilder(object):
    #XXX: ugly and inflexible
    def __init__(self, repo, base_commit, time=None, local_time=True, author=None, **extra):
        self.repo = repo
        self.base_commit = base_commit
        self.extra = extra
        self.contents = {}
        self.renames = []

        if time is None:
            time = datetime.now()
        self.author = author.strip() # normalize whitespace
        self.time = time
        self.time_local = local_time

        timetuple = time.timetuple()

        self.time_unix = unixtime.mktime(timetuple)
        # timetuple[8] is the daylight saving flag
        # its -1 for normal datetimes
        # XXX: the current logic is flawed cause it only thinks about localtime
        # XXX: should it be extended to properly deal
        #      with user defined timezones via pytz/dateutil?
        #if timetuple[8] == 1 and unixtime.daylight:
        #    self.time_offset = unixtime.altzone
        #else:
        #XXX: ignores daylight saving
        self.time_offset = unixtime.timezone

    def write(self, path, content):
        self.contents[path] = content

    def read(self, path):
        if path in self.contents:
            return self.contens[path]
        for source, dest in sorted(self.renames, reverse=True):
            if path.startswith(dest):
                path = path.replace(dest, source) #XXX: incorrect, 
        return self.base_commit.file_content(path)


    def remove(self, path):
        pass

    def mkdir(self, path):
        #XXX: only relevant for vcs's that care
        pass

    def rename(self, source, dest):
        self.renames.append((source, dest))
        for name, content in self.contents.items():
            if name.startswith(source): #XXX: incorrect
                self.contents[name.replace(source, dest)] = content
                del self.contents[name]


    def commit(self):
        raise NotImplementedError

    def __enter__(self): 
        return RevisionBuilderPath(self.base_commit, "/", self)

    def __exit__(self, etype,  eval, tb):
        if etype is None: 
            self.commit()


class RevisionBuilderPath( object):
    def __init__( self, commit, path, builder):
        self.commit = commit
        self.path = path
        self.builder = builder


    def mkdir(self):
        self.builder.mkdir(self.path)

    def rename(self , new_name):
        new = self.parent().join(new_name)
        assert self.path != '/' and new_name != '/'
        self.builder.rename(self.path, new.path)
        #XXX: shoould self.path change?

    def parent(self):
        return RevisionBuilderPath(self.commit, dirname(self.path), self.builder)

    def join(self,  path):
        return RevisionBuilderPath(self.commit, join(self.path, path), self.builder)

    def open(self,  mode='r'):
        #implement in terms of read/write
        if mode ==  'r':
            raise NotImplementedError
        elif mode == 'w':
            #XXX: test and implement all flavors of reopening
            return FileBuilder(path=self)

    def write(self, data):
        self.builder.write(self.path, data)

    def read(self):
        return self.builder.read(self.path)

    def check(self):
        try:
            self.read() #XXX: less expensive?
            return True
        except IOError:
            return False


class FileBuilder(MemoryFile):
    def __exit__(self, et, ev, tb):
        # subvertpy file data transfer doesn't seek back
        self.path.write(self.getvalue())
