import py

repo_class = 'anyvc.git.repo:GitRepository'
workdir_class = 'anyvc.git.workdir:Git'

features = [
    'dvcs',
    'wd:heavy',
]

required_tools = ['git']
required_modules = ['dulwich']

base_dirs = [
    'objects',
    'hooks',
    'info',
]

def has_git_base_dirs(path):
    return all(path.join(x).check(dir=1) for x in base_dirs)

def is_workdir(path):
    #XXX better check
    git = path.join('.git')
    return git.check(dir=1) and has_git_base_dirs(git)

def is_repository(path):
    if not isinstance(path, py.path.local):
        if path.startswith('git://'):
            #XXX: check if true
            return True
        elif 'github' in path:
            #XXX more trouble probably
            return True
        path = py.path.local(path)
    return has_git_base_dirs(path) or has_git_base_dirs(path/'.git')
