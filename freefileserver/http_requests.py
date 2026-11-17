import re

CRLF = "\r\n"
HEADER_SEP = CRLF * 2


FULL_HTTP_REQ_REGEX = re.compile(
    r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)\s+HTTP\/(\d\.\d)\r?\n"
    r"(?:[A-Za-z0-9-]+:\s*[^\r\n]*\r?\n)*"
    r"\r?\n"
    r"([\s\S]*)$"
)


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
        self.raw = raw_request
        self.invalid = not self.valid()
        if self.invalid:
            return
        parser = HttpRequestParser(raw_request)
        self.top = parser.top
        self.fields = parser.fields
        self.content = parser.content

        self.method = parser.method
        self.uri = parser.reqpath
        self.version = parser.version

    def __getattr__(self, name):
        if not hasattr(self, "fields"):
            return None
        if name in self.fields:
            return self.fields[name]
        return None

    def valid(self):
        return FULL_HTTP_REQ_REGEX.match(self.raw)
