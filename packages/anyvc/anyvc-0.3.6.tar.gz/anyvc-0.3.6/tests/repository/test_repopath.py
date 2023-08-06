from __future__ import with_statement

def test_write_direct(repo):
    with repo.transaction(author='test', message='test') as root:
        root.join('test.txt').write('test')

def test_write_file(repo):
    with repo.transaction(author='test', message='test') as root:
        with root.join('test.txt').open('w') as file:
            file.write('test')
