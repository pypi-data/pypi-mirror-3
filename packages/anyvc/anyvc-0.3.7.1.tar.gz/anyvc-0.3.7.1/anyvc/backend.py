"""
    Anyvc Backend loading abstraction

    '

    :license: LGPL2
    :copyright: 2009 by Ronny Pfannschmidt
"""

import py
from anyvc.util import cachedproperty

class Backend(object):
    def __init__(self, name, module_name):
        self.name = name
        self.module_name = module_name

    def __repr__(self):
        return '<anyvc backend %s>' % (self.name,)

    def _import(self, name):
        module, attr = name.split(':')
        impl_module = __import__(module, fromlist=['*'])
        return getattr(impl_module, attr)

    def is_workdir(self, path):
        return self.module.is_workdir(path)

    def is_repository(self, path):
        return self.module.is_repository(path)

    @cachedproperty
    def module(self):
        return __import__(self.module_name, fromlist=['*'])

    @cachedproperty
    def features(self):
        return set(self.module.features)

    @cachedproperty
    def Repository(self):
        return self._import(self.module.repo_class)

    @cachedproperty
    def Workdir(self):
        return self._import(self.module.workdir_class)

    @property
    def required_tools(self):
        return self.module.required_tools

    def missing_tools(self):
        return [tool for tool in self.required_tools
                if not py.path.local.sysfind(tool)]

    @property
    def required_modules(self):
        return self.module.required_modules

    def missing_modules(self):
        def tryimport(name):
            try:
                return __import__(name)
            except ImportError:
                pass

        return [module for module in self.required_modules
                if not tryimport(module)]
