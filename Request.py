class Request:
    def __init__(self, method, target, version, rfile):
        self.method = method
        self.target = target
        self.version = version
        self.rfile = rfile
