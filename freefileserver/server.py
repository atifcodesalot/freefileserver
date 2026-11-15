from .response_builder import HttpResponseBuilder, http
from .http_requests import *
import asyncio
import os




class FileHttpServer:
    http_version = 1.1
    def __init__(self, ipv4addr, port, path):
        self.ipv4addr = ipv4addr
        self.port = port
        self.path = path

        self.init_filesys(root=self.path)

        self.clients = dict()
        self.http_helper = HttpHelper(self)
        
        # constant response headers
        self.const_headers = {
            "Server"            
        }


    def init_filesys(self, root):
        if root == self.path:
            self.resources = set()
        for e in os.scandir(root):
            if e.is_dir():
                self.init_filesys(e.path)
            elif e.is_file():
                self.resources.add(e.path)

    def start_listening(self):
        self.socket.bind((self.ipv4addr, self.port))
        self.socket.listen(1024)
        
    

    def build_response(self, request) -> str:
        builder = HttpResponseBuilder()
        return builder.build()

    async def await_clients(self):
        reader, writer = await asyncio.open_connection(self.ipv4addr, self.port)
        client_addr = writer.get_extra_info("peername")
        self.clients[client_addr] = (reader, writer)

    async def serve_client(self, client_addr):
        # fetch the stream objects
        reader, writer = self.clients[client_addr]
        request = await reader.read(1024)
        parsed = HttpRequest(request.decode())
        response = self.build_response(parsed)
        writer.write(response)
        await writer.drain()

    async def end_client_conn(self, client_addr):
        _, writer = self.clients[client_addr]
        writer.close()


class HttpHelper:
    def __init__(self, server: FileHttpServer):
        self.server = server
    
    def get_response_params(self, req: HttpRequest):
        status = http.HTTPStatus(200)
        version = "HTTP/" + self.server.http_version
        if req.reqpath not in self.server.resources:
            status = http.HTTPStatus(404)
            content = None
        else:
            content = self.server.resources[req.reqpath]
            
        header_fields = self.get_header_fields(content)
        
        return status, version, content, header_fields
    
    def get_header_fields(self, status, content):
        fields = {}
        
        if content:
            fields["Content-Length"] = str(len(content))
        
        return fields

        
        
    

        
            
            