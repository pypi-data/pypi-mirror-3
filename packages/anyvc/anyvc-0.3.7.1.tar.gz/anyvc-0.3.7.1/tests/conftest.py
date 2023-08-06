import py
from tests.helpers import  VcsMan
import os

from anyvc import metadata

pytest_plugins = "doctest"

test_in_interpreters = 'python2', 'python3', 'jython', 'pypy'



def pytest_addoption(parser):
    g = parser.getgroup('anyvc')
    g.addoption("--local-remoting", action="store_true", default=False,
               help='test via execnet remoting')
    g.addoption("--no-direct-api", action="store_true", default=False,
                help='don\'t test the direct api')
    g.addoption("--vcs", action='store', default=None)

def pytest_configure(config):
    vcs = config.getvalue('vcs')
    if vcs is None:
        return
    vcs = vcs.split('-')[0]
    if vcs not in metadata.backends:
        if vcs in metadata.aliases:
            vcs = metadata.aliases[vcs]
            config.option.vcs = vcs
        else:
            raise KeyError(vcs, '%r not found' % vcs)


    os.environ['BZR_EMAIL'] = 'Test <test@example.com>'

funcarg_names = set('mgr repo wd backend'.split())

def pytest_generate_tests(metafunc):
    if not funcarg_names.intersection(metafunc.funcargnames):
        return
    specs = []
    if not metafunc.config.getvalue('no_direct_api'):
        specs.append(('direct', None))
    if metafunc.config.getvalue('local_remoting'):
        specs.append(('remote', 'popen'))
    #XXX: ssh?

    ids, values = zip(*specs)
    metafunc.parametrize('spec', values, ids=ids, indirect=True)
    wanted = metafunc.config.getvalue('vcs')
    if wanted:
        backends =[x for x in metadata.backends if x==wanted]
    else:
        backends = list(metadata.backends)
    metafunc.parametrize('vcs', backends, indirect=True)

def pytest_funcarg__spec(request):
    return request.param

def pytest_funcarg__vcs(request):
    return request.param

def pytest_funcarg__backend(request):
    """
    create a cached backend instance that is used the whole session
    makes instanciating backend cheap
    """
    vcs = request.getfuncargvalue('vcs')
    spec = request.getfuncargvalue('spec')
    return request.cached_setup(
            lambda: metadata.get_backend(vcs, spec),
            extrakey=(vcs, spec),
            scope='session')


def pytest_funcarg__mgr(request):
    """
    create a preconfigured :class:`tests.helplers.VcsMan` instance
    pass the currently tested backend 
    and create a tmpdir for the vcs/test combination

    auto-check for the vcs features and skip if necessary
    """
    spec = request.getfuncargvalue('spec')
    r = spec or 'local'
    testdir = request.getfuncargvalue('tmpdir')
    backend = request.getfuncargvalue('backend')

    required_features = getattr(request.function, 'feature', None)

    if required_features:
        required_features = set(required_features.args)
        difference = required_features.difference(backend.features)
        print required_features
        if difference:
            py.test.skip('%s lacks features %r' % (backend, sorted(difference)))

    return VcsMan(backend.name, testdir, spec, backend)

def pytest_funcarg__repo(request):
    """
    create a repo below mgf called 'repo'
    """
    return request.getfuncargvalue('mgr').make_repo('repo')

def pytest_funcarg__wd(request):
    """
    create a workdir below mgr called 'wd'
    if the feature "wd:heavy" is not supported use repo as help
    """
    mgr = request.getfuncargvalue('mgr')
    if 'wd:heavy' not in mgr.backend.features:
        repo = request.getfuncargvalue('repo')
        wd = mgr.create_wd('wd', repo)
    else:
        wd = mgr.create_wd('wd')

    fp = request.function
    if hasattr(fp, 'files'):
        files = fp.files.args[0]
        wd.put_files(files)
        assert wd.has_files(*files)
        if  hasattr(fp, 'commit'):
            wd.add(paths=list(files))
            wd.commit(message='initial commit')
    return wd


def pytest_collect_directory(path, parent):
    for compiled_module in path.listdir("*.pyc"):
        if not compiled_module.new(ext=".py").check():
            compiled_module.remove()

