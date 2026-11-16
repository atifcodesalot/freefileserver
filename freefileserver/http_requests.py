import mimetypes
import regex

CRLF = "\r\n"
HEADER_SEP = CRLF * 2


REQ_HEADER_REGEX = r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)\s+HTTP\/(\d\.\d)$"


class HttpRequestParser:
    def __init__(self, raw_request: str):
        self.raw_request = raw_request
        self.parse()

    def parse(self):
        header, fields_raw = self.raw_request.split(HEADER_SEP)
        self.header = header
        self.parse_header()
        self.fields_raw = fields_raw
        self.parse_fields()

    def parse_fields(self):
        self.fields = dict()
        fields_list = self.fields_raw.split(CRLF)
        # construct fields
        for field in fields_list:
            field_id, field_val = field.split(": ")
            self.fields[field_id] = field_val

    def parse_header(self):
        self.method, self.reqpath, self.version = self.header.split(" ")


class HttpRequest:
    def __init__(self, raw_request: str):
        parser = HttpRequestParser(raw_request)

        self.header = parser.header
        self.fields = parser.fields
        
        self.method = parser.method
        self.uri = parser.reqpath
        self.version = parser.version
        

    def valid_header(self):
        return regex.match(REQ_HEADER_REGEX, self.header) is not None
    
    def valid_fields(self):
        pass
