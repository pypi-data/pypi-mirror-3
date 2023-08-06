from __future__ import with_statement
import os

from anyvc.common.workdir import CommandBased, relative_to, WorkDirWithParser
from subprocess import call
#from subvertpy import client, wc, ra, NODE_DIR

#from subvertpy.ra import RemoteAccess, Auth, get_username_provider, SubversionException

class SubVersion(CommandBased):
    #XXX: disabled
    cmd = "svn"
    detect_subdir = ".svn/props"
    repository = None # no local repo


    def create(self):
        raise NotImplementedError('no havy workdirs')

    def get_status_args(self, recursive, paths, **kw):
        #TODO: figure a good way to deal with changes in external
        # (maybe use the svn python api to do that)
        ret = ["st", "--no-ignore", "--ignore-externals", "--verbose"]
        if not recursive:
            ret.append("--non-recursive")
        return ret + list(paths)


    def create_from(self, source):
        from urllib import quote
        source = quote(str(source))
        call(['svn', 'co', 'file://%s' % source, self.path.strpath])

    state_map = {
            "?": 'unknown',
            "A": 'added',
            " ": 'clean',
            "!": 'missing',
            "I": 'ignored',
            "M": 'modified',
            "D": 'removed',
            "C": 'conflict',
            'X': 'clean',
            'R': 'modified',
            '~': 'clean',
            }

    def get_add_args(self, paths, **kw):
        # svn add doesnt add parent dirs by default
        return ['add', '--parents'] + paths

    def get_diff_args(self, paths=(), **kw):
        return ['diff', '--diff-cmd', 'diff'] + list(paths)

    def get_rename_args(self, source, target):
        return ['move', source, target]

    def parse_status_item(self, item, cache):
        if item[0:4] == 'svn:':
            # ignore all svn error messages
            return None
        state = item[0]
        file = item.split()[-1]
        if file == '.':
            # this is the path of the repo
            # normalize to ''
            file = ''
        #TODO: handle paths with whitespace if ppl fall in that one
        return self.state_map[state], file





class BrokenSubversion(object):  # workdir with parser
    detect_subdir= '.svn/entries'
    repository = None # no local repo

    def create_from(self, source):
        #XXX: omg what a fucked up mess
        r = ra.RemoteAccess('file://' + source)
        rev = r.get_latest_revnum()
        print rev
        import os
        #XXX: wth are we doing here
        os.mkdir(self.path)
        c = client.Client(auth=Auth([get_username_provider()]))
        c.checkout('file://' + source, self.path, rev)

    def add(self, paths=None, recursive=False):
        #XXX: recursive
        import os
        #XXX: hacl
        print paths
        w = wc.WorkingCopy(
                path=self.path,
                write_lock=True,
                associated=None)
        for path in paths:
            segments = path.split(os.path.sep)
            p = self.path
            for segment in segments:
                p = os.path.join(p, segment)
                print p, w.add(path=p)

        w.close()

    def commit(self, paths=None, message=None, user=None):
        if paths:
            targets = [os.path.join(self.path, path) for path in paths]
        else:
            targets = [self.path]
        c = client.Client(auth=Auth([get_username_provider()]))

        def m(items):
            print items
            print message
            return message #XXX: encoding
        c.log_msg_func = m
        c.commit(targets=targets, recurse=True)

    def walk_status(self, parent, basename):
        basepath = os.path.join(self.path, basename)
        w = wc.WorkingCopy(parent, basepath)
        e = w.entries_read(True)
        print e.keys()
        for name, entry in e.items():
            if not name: #ignore root for now
                continue 
            yield os.path.join(basename, name), entry
            if entry.kind == NODE_DIR:
                for item in self.walk_status(w, os.path.join(basename, name)):
                    yield item
        others = os.listdir(basepath)

        for item in others:
            if item=='.svn' or item in e:
                continue
            print item
            yield os.path.join(basename, item), None #unknown


    def status_impl(self,paths=(), recursive=True):
        return self.walk_status(None, '') #xxx: set limits?

    def parse_status_item(self, item, cache):
        name, e = item
        if e is None:
            return 'unknown', name
        print e.kind, e.schedule, repr(e.name)
        map = {
            wc.SCHEDULE_ADD: 'added',
            wc.SCHEDULE_DELETE: 'removed',
            wc.SCHEDULE_NORMAL: 'clean',
        }
        state = map[e.schedule]
        full_path = os.path.join(self.path, name)
        if not os.path.exists(full_path) and state!='removed':
            return 'missing', name
        print state, name
        if state=='clean':
            import hashlib
            with open(os.path.join(self.path, name)) as f:
                if hashlib.md5(f.read()).hexdigest()!=e.checksum:
                    return 'modified', name

        return state, name

