import py

workdir_class = 'anyvc.subversion.workdir:SubVersion'
repo_class = 'anyvc.subversion.repo:SubversionRepository'

features = [
    'wd:light',
]


required_tools = ['svn']
required_modules = ['subvertpy']


def is_workdir(path):
    svn = path.join('.svn')
    return svn.join('entries').check() \
       and svn.join('props').check(dir=1) \
       and svn.join('text-base').check(dir=1)


def is_repository(path):
    if not isinstance(path, py.path.local):
        if path.startswith('svn://'):
            return True
        elif path.startswith('http+svn'):
            return True

    path = py.path.local(path)

    return path.join('format').check() \
       and path.join('hooks').check(dir=1) \
       and path.join('locks').check(dir=1) \
       and path.join('format').read().strip().isdigit()
