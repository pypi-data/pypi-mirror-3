"""
This Crosswalk query type has been deprecated.  Crosswalk is now available
through the regular table read API.
"""

from read import Read
import warnings

class Crosswalk(Read):
    def __init__(self, api, params={}):
        Read.__init__(self, api, 'places/crosswalk', params)

    def factual_id(self, factual_id):
        warnings.warn('This method has been deprecated.  Please use row filters instead.', DeprecationWarning)
        return self._copy({'factual_id': factual_id})

    def limit(self, max_rows):
        return self._copy({'limit': max_rows})

    def only(self, namespaces):
        warnings.warn('This method has been deprecated.  Please use row filters instead.', DeprecationWarning)
        return self._copy({'only': namespaces})

    def include_count(self, include):
        return self._copy({'include_count': include})

    def namespace(self, namespace, namespace_id):
        warnings.warn('This method has been deprecated.  Please use row filters instead.', DeprecationWarning)
        return self._copy({'namespace': namespace, 'namespace_id': namespace_id})

    def _copy(self, params):
        return Crosswalk(self.api, self.merge_params(params))
