import py
from anyvc.remote import RemoteBackend
from anyvc.metadata import backends

def test_end_popen_backend(backend):
    backend = RemoteBackend(backend.name, backends[backend.name], 'popen')
    assert backend.active
    backend.stop()
    assert not backend.active

def test_missing_backend_failure(monkeypatch):
    print backends
    py.test.raises(ImportError, RemoteBackend, 'testvc', '_missing_', 'popen')
