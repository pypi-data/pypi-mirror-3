
import py
from anyvc.metadata import backends, get_backend

def test_get_backend(backend, mgr):
    assert backend.module_name == backends[mgr.vc]


def test_has_features(backend):
    assert isinstance(backend.features, set)


def test_has_working_repository_check(repo, backend):
    print repo.path
    assert backend.is_repository(repo.path)


def test_has_working_workdir_check(wd, backend):
    print wd.path
    assert backend.is_workdir(wd.path)

def test_required_tools(backend):
    
    # just to cause failures on missing data
    backend.required_tools

    assert not backend.missing_tools()

def test_required_modules(backend):
    # just to cause failures on missing data
    backend.required_modules

    assert not backend.missing_modules()

