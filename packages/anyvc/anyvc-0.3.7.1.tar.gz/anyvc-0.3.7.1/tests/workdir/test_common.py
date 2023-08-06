"""
    this is a series of functional tests
    each begins at a given state and runs a series of actions,
    asserting the workdir state between each
"""


# copyright 2008 by Ronny Pfannschmidt
# license lgpl2 or later
import py


has_files = py.test.mark.files({
        'test.py':'print "test"',
        })

commited = py.test.mark.commit

@has_files
def test_workdir_add(wd):
    """
    * add a unknown file
    * commit it
    """

    wd.check_states(unknown=['test.py'])
    print wd.add(paths=['test.py'])
    wd.check_states(added=['test.py'])
    print wd.commit(paths=['test.py'], message='add test.py')
    wd.check_states(clean=['test.py'])

def test_subdir_state_add(wd):
    """
    * add a file in a subdir
    """
    wd.put_files({
        'subdir/test.py':'test',
    })

    print wd.add(paths=['subdir/test.py'])
    wd.check_states(added=['subdir/test.py'])
    print wd.commit(message='add subdir/test.py')
    wd.check_states(clean=['subdir/test.py'])


@has_files
@commited
def test_workdir_remove(wd):
    """
    * remove a known file
    * commit the removal
    """
    wd.check_states(clean=['test.py'])
    wd.remove(paths=['test.py'])
    wd.check_states(removed=['test.py'])
    wd.commit(message='*')

    py.test.raises(AssertionError,wd.check_states, clean=['test.py'])
    assert not wd.path.join('test.py').check()


@has_files
@commited
def test_workdir_rename(wd):
    """
    * rename a known file
    * check the add/remove pair
    * commit
    """
    wd.rename(source='test.py', target='test2.py')
    wd.check_states(
        removed=['test.py'],
        added=['test2.py'],
    )

    wd.commit(message='renamed')
    wd.check_states(clean=['test2.py'])


@has_files
@commited
def test_workdir_revert(wd):
    """
    * remove a known file (vcs command)
    * revert
    * change the content of a known file
    * revert
    """
    wd.remove(paths=['test.py'])
    wd.check_states(removed=['test.py'])

    wd.revert(paths=['test.py'])
    wd.check_states(clean=['test.py'])

    wd.put_files({
        'test.py':'oooo'
        })

    wd.check_states(modified=['test.py'])

    wd.revert(paths=['test.py'])
    wd.check_states(clean=['test.py'])


@has_files
def test_diff_all(wd):
    """
    * change a known file
    * check the diff
    """
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    wd.put_files({
        'test.py':'ooo'
    })

    diff = wd.diff()
    print diff
    assert 'ooo' in diff
    assert 'print "test"' in diff


@has_files
@commited
def test_file_missing(wd):
    """
    * delete a known file (just in the workdir)
    * check the missing state
    """
    wd.delete_files('test.py')
    wd.check_states(missing=['test.py'])


@has_files
@commited
def test_status_subdir_only(wd):
    """
    * add a file in a subdir
    * commit
    * change the file in the subdir
    * check status for the subdir only returning items of that subdir
    """
    wd.put_files({
        'subdir/a.py':'foo\n',
        })
    wd.add(paths=['subdir/a.py'])
    wd.check_states(added=['subdir/a.py'])

    print wd.commit(message='add some subdir')

    wd.check_states(clean=['subdir/a.py'])
    wd.put_files({
        'subdir/a.py':'bar\nfoo\n', #XXX: different size needed for hg status
        })

    stats = list(wd.status(paths=['subdir']))
    assert any(s.relpath == 'subdir/a.py' for s in stats)

    wd.check_states(modified=['subdir/a.py'])


@has_files
@commited
def test_workdir_open(wd, backend):
    """
    check if anyvc.workdir.open works as expected
    """
    import anyvc
    wd2 = anyvc.workdir.open(wd.path)
    assert backend.is_workdir(wd2.path)




@has_files
@commited
def test_workdir_open_honors_ANYVC_IGNORED_WORKDIRS(monkeypatch, wd):
    """
    check that :func:`anyvc.workdir.open` honors `ANYVC_IGNORED_WORKDIRS`
    """
    import anyvc
    assert anyvc.workdir.open(wd.path) is not None
    monkeypatch.setenv('ANYVC_IGNORED_WORKDIRS', wd.path)
    assert anyvc.workdir.open(wd.path) is None


def test_disallowed_paths(monkeypatch):
    from anyvc._workdir import _disallowd_workdirs
    monkeypatch.setenv('ANYVC_IGNORED_WORKDIRS', '/a:/b')
    dirs = _disallowd_workdirs()
    assert '/a' in dirs
    assert '/b' in dirs
    monkeypatch.setenv('ANYVC_IGNORED_WORKDIRS', '~')
    dirs = _disallowd_workdirs()
    assert py.std.os.environ['HOME'] in dirs

