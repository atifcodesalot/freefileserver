
import regex

CRLF = "\r\n"
HEADER_SEP = CRLF * 2


REQ_HEADER_REGEX = r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)\s+HTTP\/(\d\.\d)$"


class HttpRequestParser:
    def __init__(self, raw_request: str):
        self.raw_request = raw_request
        self.parse()

    def parse(self):
        self.headers, self.content = self.raw_request.split(HEADER_SEP)
        self.top, *self.fields_raw = self.headers.split(CRLF)
        self.parse_header_top()
        self.parse_fields()

    def parse_fields(self):
        self.fields = dict()
        
        # construct fields
        for field in self.fields_raw:
            if not field: 
                continue
            field_id, field_val = field.strip().split(": ")
            self.fields[field_id] = field_val

    def parse_header_top(self):
        self.method, self.reqpath, self.version = self.top.split(" ")


class HttpRequest:
    def __init__(self, raw_request: str):
        parser = HttpRequestParser(raw_request)

        self.top = parser.top
        self.fields = parser.fields
        self.content = parser.content
        
        self.method = parser.method
        self.uri = parser.reqpath
        self.version = parser.version
        
        self.invalid = not self.valid()
        
    def __getattr__(self, name):
        return self.fields[name]
    
    def valid(self):
        return self.valid_header_top() and self.valid_fields()

    def valid_header_top(self):
        return regex.match(REQ_HEADER_REGEX, self.top) is not None
    
    def valid_fields(self):
        # TODO: implement this
        return True
