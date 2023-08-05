import urlparse

class Request(object):
    def __init__(self, client_address, command, path, request_version, headers):
        self.client_address = client_address
        self.command = command
        self.path = path
        self.request_version = request_version
        self.headers = headers
        self.GET = self.parse_GET(self.path)
    
    @classmethod
    def parse_GET(cls, path):
        parts = urlparse.urlparse(path)
        ret = {}
        for k, l in urlparse.parse_qs(parts.query, keep_blank_values=True).iteritems():
            ret[k] = l[0]
        return ret
    

class Response(object):
    def __init__(self, code, body, content_type=None, location=None):
        self.code = code
        self.body = body
        self.content_type = content_type
        self.location = location

