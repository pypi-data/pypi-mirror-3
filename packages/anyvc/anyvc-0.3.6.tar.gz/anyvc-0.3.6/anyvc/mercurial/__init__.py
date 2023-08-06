import py

from anyvc.util import http_code_content

repo_class = 'anyvc.mercurial.repo:MercurialRepository'
workdir_class = 'anyvc.mercurial.workdir:Mercurial'

features = [
    'dvcs',
    'wd:heavy',
]

required_tools = []
required_modules = ['mercurial']

def is_hg(path):
    return path.join('.hg/store').check(dir=1) \
       and path.join('.hg/requires').check()


is_workdir = is_hg

def is_repository(path):
    if isinstance(path, py.path.local) \
        or ('://' not in path and
            not path[:3] == 'bb:'):
        path = py.path.local(path)
        return is_hg(path)
    else:
        if path[:4] == 'http':
            code, content = http_code_content(path+'?cmd=capabilities')
            if code == 200:
                return 'unbundle=' in content
        elif path[:4] == 'ssh':
            return False
            raise RuntimeError('ssh check not propperly implemented')
        else:
            return False
            raise RuntimeError('unknown kind of path ' + str(path))

