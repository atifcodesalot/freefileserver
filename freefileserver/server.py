

from .files import FileHelper, os
from .response_builder import HttpResponseBuilder, http
from .http_requests import *
import asyncio
import urllib
import mimetypes

from . import logger

class FileHttpServer:
    http_version = 1.1

    def __init__(self, ipv4addr, port, root_path):
        self.ipv4addr = ipv4addr
        self.port = port
        self.root_path = root_path

        self.pwd = root_path

        self.clients = dict()
        self.http_helper = HttpHelper(self)
        self.file_helper = FileHelper(self)

        # constant response headers
        self.const_headers = {"Server"}

    def start_listening(self):
        self.socket.bind((self.ipv4addr, self.port))
        self.socket.listen(1024)

    def build_response(self, request: HttpRequest) -> str:
        builder = HttpResponseBuilder()
        return builder.build()

    async def start(self):
        self.server = await asyncio.start_server(
            self.serve_client, self.ipv4addr, self.port
        )
        logger.info("Now serving")
        async with self.server:
            await self.server.serve_forever()

    async def serve_client(self, reader, writer):
        request = await reader.read(1024)
        parsed = HttpRequest(request.decode())
        response = self.build_response(parsed)
        writer.write(response)
        await writer.drain()

    async def end_client_conn(self, client_writer):
        client_writer.close()
        await client_writer.wait_closed()

    def run(self):
        asyncio.run(self.start())


class HttpHelper:
    HTML_404 = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>404 Not Found</title>
            </head>
            <body>
                <h1>404 Not Found</h1>
                <p>The requested resource was not found on this server.</p>
            </body>
            </html>
    """

    def __init__(
        self,
        server: FileHttpServer,
        allowed=[
            "GET",
        ],
    ):
        self.server = server
        self.allowed = allowed

    @staticmethod
    def erronous_status(status: http.HTTPStatus):
        return status.value >= 400

    def get_status(self, req: HttpRequest):
        if req.method.upper() not in self.allowed:
            return http.HTTPStatus.METHOD_NOT_ALLOWED
        elif not self.server.file_helper.search_file(req.uri):
            return http.HTTPStatus.NOT_FOUND

    def get_response_params(self, req: HttpRequest):
        version = self.get_version()
        status = self.get_status(req)
        content, _type = self.get_content(req)
        headers: dict = self.get_header_fields(status, content)
        
        return status, version, content, headers
        

    def get_version(self):
        return "HTTP/" + self.server.http_version

    def handle_error_content(self, status):
        content = None
        if status is http.HTTPStatus.NOT_FOUND:
            content = self.HTML_404
        return content, mimetypes.types_map['.html']
    
    def get_content(self, req: HttpRequest):
        if self.erronous_status(req.status):
            return self.handle_error_content(req.status)
        
        file_helper = self.server.file_helper
        file = file_helper.search_file(req.uri)
        return file.read(), self.get_mimetype()
        

    def get_header_fields(self, status, content, req):
        fields = {}

        if content:
            fields["Content-Length"] = str(len(content))
            fields["Content-Type"] = self.get_mimetype(req)

        elif status is http.HTTPStatus.METHOD_NOT_ALLOWED:
            fields["Allow"] = ", ".join(self.allowed)

        return fields
    
    def get_mimetype(self, req):
        filename = self.get_filename(req.uri)
        ext = self.server.file_helper.get_file_ext(filename)
        return mimetypes.types_map[ext]
        
    
    def to_filepath(self, uripath: str):
        normpath = os.path.normpath(uripath)
        return normpath.replace('/', os.sep)
    
    def get_filename(self, uri):
        parsed = urllib.parse.urlparse(uri)
        filepath = os.path.normpath(parsed.path)
        return os.path.basename(filepath)
        
