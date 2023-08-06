
#XXX: ValueError for backward compat, figure how to phase out later
class NotFoundError(LookupError, ValueError):
    """raised if a repo/workdir cant be found"""
    def __init__(self, vc, path):
        Exception.__init__(self, vc, path)
        self.vc = vc
        self.path = path

    def __str__(self):
        return "%(vc)s repo not found for %(path)r"%vars(self)
