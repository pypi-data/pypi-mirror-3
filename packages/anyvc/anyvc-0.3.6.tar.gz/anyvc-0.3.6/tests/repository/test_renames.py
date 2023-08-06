from __future__ import with_statement
import py

def test_rename_simple(repo):

    with repo.transaction(message='create', author='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write('test')

    with repo.get_default_head() as root:
        assert root.join('test.txt').exists()

    with repo.transaction(message='rename', author='test') as root:
        #XXX: check if relative names are ok for rename in the fs api
        root.join('test.txt').rename('test_renamed.txt')

    with repo.get_default_head() as root:
        assert not root.join('test.txt').exists()
        assert root.join('test_renamed.txt').exists()


@py.test.mark.xfail(reason='not implemented', run=False)
def test_rename_directory(repo):

    with repo.transaction(message='create', author='test') as root:
        dir = root.join('testdir')
        dir.mkdir()
        with dir.join('test.txt').open('w') as f:
            f.write('test')

    with repo.get_default_head() as root:
        assert root.join('testdir/test.txt').exists()

    with repo.transaction(message='rename', author='test') as root:
        #XXX: check if relative names are ok for rename in the fs api
        root.join('testdir').rename('testdir2')

    with repo.get_default_head() as root:
        assert not root.join('testdir/test.txt').exists()
        assert root.join('testdir2/test.txt').exists()

