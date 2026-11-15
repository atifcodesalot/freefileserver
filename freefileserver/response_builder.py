

from .http_requests import HttpRequest, CRLF, HEADER_SEP
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
        if self.content:
            dumped += CRLF + self.content
        return dumped.encode(encoding)
            
    

class HttpResponseBuilder:
    def __init__(self, status_code, version, content, **header_fields):
        self.status_code = status_code
        self.version = version
        self.content = content
        self.header_fields = header_fields
    
    def build(self, encoding) -> str:
        headers_list = self.header_fields.values()
        response = HttpResponse(http.HTTPStatus(self.status_code), 
                                self.version, headers_list, self.content)
        return response.encode(encoding=encoding)
    
    def handle_request_header(self, header: str):
        pass
        
    def build_header(self):
        pass