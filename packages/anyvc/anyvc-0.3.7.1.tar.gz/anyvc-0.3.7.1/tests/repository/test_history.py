from __future__ import with_statement
import py
from datetime import datetime


def test_build_first_commit(repo):
    with repo.transaction(message='initial', author='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write("text")

    head = repo.get_default_head()
    with head as root:
        with root.join("test.txt").open() as f:
            content = f.read()
            assert content == 'text'

    if not isinstance(head.id, int):
        hre = py.std.re.compile('\w+')
        assert hre.match(head.id), 'rev id is messed goo %r'%head.id

def test_generate_commit_chain(repo):
    for i in range(1,11):
        with repo.transaction(
                message='test%s'%i,
                author='test') as root:
            with root.join('test.txt').open('w') as f:
                f.write("test%s"%i)

    assert len(repo) == 10

    head = repo.get_default_head()

    revs = [head]
    rev = head

    while rev.parents:
        rev = rev.parents[0]
        revs.append(rev)

    assert len(revs) == 10

    for i, rev in enumerate(reversed(revs)):
        with rev as root:
            with root.join('test.txt').open() as f:
                data = f.read()
                assert data == 'test%s'%(i+1)


def test_create_commit_at_time(mgr, repo):
    if mgr.vc == 'subversion':
        py.test.skip('currently no support for setting the commit time on svn')

    time = datetime(2000, 1, 1, 10, 0, 0)

    with repo.transaction(
            message='test',
            author='test',#XXX: author should be optional
            time=datetime(2000, 1, 1, 10, 0, 0)) as root:
        with root.join('test.txt').open('w') as f:
                f.write('test')

    head = repo.get_default_head()

    print repr(head.id)
    print head.time
    assert head.time == time


def test_create_commit_with_author(mgr):
    if mgr.vc == 'subversion':
        py.test.skip('currently no support for setting the commit author on svn')

    repo = mgr.make_repo('repo')

    with repo.transaction(
            message='test',
            author='test author ', #with whitespace
            ) as root:
        with root.join('test.txt').open('w') as f:
                f.write('test')

    head = repo.get_default_head()
    print repr(head.author)
    assert head.author == 'test author' #whitespace gone

def test_isdir(repo):
    with repo.transaction(
            message='test',
            author='test') as root:
        with root.join('testdir/test.txt').open('w') as f:
            f.write("test")

    head = repo.get_default_head()
    assert head.isfile("/testdir/test.txt")
    assert not head.isfile("/not_test.txt")
    assert head.isdir("/")
    assert head.isdir("/testdir")
    # None-existant directories alphabetically before and after /testdir:
    assert not head.isdir("/aaa")
    assert not head.isdir("/xxx")
