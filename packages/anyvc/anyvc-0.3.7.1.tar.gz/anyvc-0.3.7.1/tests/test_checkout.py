import py
import anyvc

example_remotes = {
    'mercurial': 'http://bitbucket.org/hpk42/apipkg/',
    'git': 'git://github.com/',
    'subversion': 'http+svn://bitbucket.org/hpk42/apipkg/trunk',
}


@py.test.mark.files({'setup.py': 'pass'})
@py.test.mark.commit
@py.test.mark.feature('wd:light')
def test_checkout_local(repo, wd, mgr):
    path = mgr.base/'checkout'

    wd2 = anyvc.workdir.checkout(
        target=path,
        source=repo.path,
        )
    assert path.join('setup.py').check()

@py.test.mark.files({'setup.py': 'pass'})
@py.test.mark.commit
@py.test.mark.feature('wd:heavy')
def test_clone_local(wd, mgr):

    path = mgr.base/'clone'

    wd2 = anyvc.workdir.clone(
        target=path,
        source=wd.path,
        )

    assert path.join('setup.py').check()

@py.test.mark.feature('wd:heavy')
def test_clone_remote(mgr):

    path = mgr.base/'clone'
    wd = anyvc.workdir.clone(
        target=path,
        source=example_remotes[mgr.backend.name],
    )

@py.test.mark.feature('wd:light')
def test_checkout_remote(backend, mgr):

    path = mgr.base/'checkout'
    wd = anyvc.workdir.checkout(
        target=path,
        source=example_remotes[mgr.backend.name],
    )
