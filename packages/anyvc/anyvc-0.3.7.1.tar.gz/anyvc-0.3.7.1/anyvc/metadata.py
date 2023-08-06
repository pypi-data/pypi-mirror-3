"""
    anyvc.metadata
    ~~~~~~~~~~~~~~

    some basic metadata about vcs states and other fun

    .. warning::

      this module is subject to huge changes
"""

def _(str):
    return str #XXX: gettext

state_descriptions = dict(
    #XXX: finish, validate
    unknown = _("not known to the vcs"),
    ignored = _("ignored by the vcs"),
    added = _("added"),
    clean = _("known by the vcs and unchanged"),
    modified =_("changed in the workdir"),
    missing = _("removed from the workdir, still recorded"),
    removed = _("removed by deletion or renaming"),
    conflicte = _("merge conflict")
)

aliases = {
    'svn': 'subversion',
    'hg': 'mercurial',
}


# known implementations

backends = {
    'mercurial': 'anyvc.mercurial',
    'git': 'anyvc.git',
    'subversion': 'anyvc.subversion'
}

def get_backends(limit_to=None,features=None):
    """
    :param limit_to: optional list of backends to try, will use all if use is none
    :type limit_to: list of string or None

    a generator over all known backends
    """
    features = set(features or ())
    use = limit_to or backends
    for backend in use:
        try:
            backend = get_backend(backend)
            if backend.features.issuperset(features):
                yield backend
        except ImportError:
            pass


def get_backend(vcs, use_remote=False):
    module = backends[vcs]

    if use_remote:
        if use_remote is True:
            use_remote = 'popen'
        from anyvc.remote import RemoteBackend
        return RemoteBackend(vcs, module, use_remote)
    else:
        from anyvc.backend import Backend
        return Backend(vcs, module)
