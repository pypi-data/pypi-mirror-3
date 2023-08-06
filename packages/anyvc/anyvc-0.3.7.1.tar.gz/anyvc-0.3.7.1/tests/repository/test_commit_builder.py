import py
from os import path
from anyvc.common.commit_builder import CommitBuilder


class FakeCommit(object):
    def __init__(self, file_tree):
        self.file_tree = file_tree
    
    def file_content(self, name):
        items = name.split(path.sep)
        tree = self.file_tree
        for item in items:
            tree = tree[item]
        return tree



def test_rename():
    base_commit = FakeCommit({
        'test':{
            'test.py':'#!/usr/bin/python',
            },
        })

    commit_builder = CommitBuilder(None, base_commit, author='test')

    commit_builder.mkdir('test2')
    commit_builder.rename('test/test.py', 'test2/test.py')

    content = commit_builder.read('test2/test.py')
    assert content == '#!/usr/bin/python'


    commit_builder.write('test2/test.py', 'test = 1')
    commit_builder.rename('test2/test.py', 'test/test.py')

