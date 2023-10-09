class Response:
    def __init__(self, status, reason, headers=None, body: str = None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body
        self.codes = {'Bad request': 400, 'Request line is too long': 414,
                      'Unexpected HTTP version': 400, 'Malformed request line': 400,
                      'Header line is too long': 414, 'Too many headers': 414,
                      'Not found': 404, 'File already exist': 409}
