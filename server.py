from .response_builder import HttpResponseBuilder
from .http_requests import *
import asyncio
import os




class FileHttpServer:
    def __init__(self, ipv4addr, port, path):
        self.ipv4addr = ipv4addr
        self.port = port
        self.path = path

        self.init_filesys(root=self.path)

        self.clients = dict()
        self.http_helper = HttpHelper(self)

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
        if req.reqpath not in self.server.resources:
            pass
            
            