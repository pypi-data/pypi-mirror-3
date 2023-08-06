"""
    anyvc
    ~~~~~~

    pythonic vcs abstractions

    :license: LPL2
    :copyright: Ronny Pfannschmidt and others
"""


import apipkg
apipkg.initpkg(__name__, {
    'workdir': {
        'clone': 'anyvc._workdir:clone',
        'checkout': 'anyvc._workdir:checkout',
        'open': 'anyvc._workdir:open',
        },
    })
