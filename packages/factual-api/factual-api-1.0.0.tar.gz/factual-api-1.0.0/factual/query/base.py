"""
Base query class
"""

class Base(object):
    def __init__(self, api, params):
        self.api = api
        self.params = params
        self.response = None

    def data(self):
        return self.get_response()['data']

    def total_row_count(self):
        return self.get_response()['total_row_count']

    def included_rows(self):
        return self.get_response()['included_rows']

    def get_url(self):
        return self.api.build_url(self.path, self.params)

    def get_response(self):
        if not self.response:
            self.response = self.api.execute(self)
        return self.response

    def merge_params(self, params):
        new_params = self.params.copy()
        new_params.update(params)
        return new_params
