

from .http_requests import CRLF, HEADER_SEP
import http
from dataclasses import dataclass


@dataclass
class HttpResponse:
    status: http.HTTPStatus
    version: str
    headers: list[str]
    content: str
    
    def dump_to_binary(self, encoding="utf-8"):
        statline = f"{self.version} {self.status.value} {self.status.name}\r\n"
        dumped = ""
        dumped += statline
        dumped += CRLF.join(self.headers)
        content_pytype = type(self.content)
        if self.content:
            if content_pytype is str:
                dumped += HEADER_SEP + self.content
        encoded = dumped.encode(encoding)
        if content_pytype is bytes:
            encoded += HEADER_SEP.encode(encoding) + self.content 
        return encoded
            
    

class HttpResponseBuilder:
    def __init__(self, status_code, version, content, **header_fields):
        self.status_code = status_code
        self.version = version
        self.content = content
        self.header_fields: dict = header_fields
    
    def build(self, encoding) -> str:
        headers_list = self.build_headers()
        response = HttpResponse(http.HTTPStatus(self.status_code), 
                                self.version, headers_list, self.content)
        return response.dump_to_binary(encoding=encoding)
        
    def build_headers(self):
        headers_list = []
        pairs = self.header_fields.items()
        for pair in pairs:
            headers_list.append(': '.join(pair))
        return headers_list
            
        