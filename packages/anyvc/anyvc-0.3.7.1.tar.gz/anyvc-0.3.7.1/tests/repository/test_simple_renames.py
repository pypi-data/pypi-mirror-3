
from __future__ import with_statement
import py

@py.test.mark.xfail
@py.test.mark.incomplete
def test_simple_rename(mgr):
    repo = mgr.make_repo('repo')
    with repo.transaction(
            message='initial conent',
            author='test',
            ) as root:
        root.join('test.py').write('test = 1\n')
    with repo.transaction(
            message='add a rename',
            author='test',
            ) as root:
        assert root.join('test.py').read() == 'test = 1\n'

        root.join('test.py').rename('test2.py')

        assert root.join('test2.py').read() == 'test = 1\n'
        assert not root.join('test.py').check()


