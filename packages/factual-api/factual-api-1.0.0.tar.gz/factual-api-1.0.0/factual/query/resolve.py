from base import Base

class Resolve(Base):
    def __init__(self, api, values={}):
        self.path = 'places/resolve'
        Base.__init__(self, api, {'values': values})

    def values(self, values):
        return self._copy({'values': values})

    def include_count(self, include):
        return self._copy({'include_count': include})

    def _copy(self, params):
        return Resolve(self.api, self.path, self.merge_params(params))
