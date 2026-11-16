from .files import FileHelper
from .response_builder import HttpResponseBuilder, http
from .http_requests import *
import asyncio
import mimetypes

from . import logger


class FileHttpServer:
    http_version = 1.1

    def __init__(self, ipv4addr, port, root_path):
        self.ipv4addr = ipv4addr
        self.port = port
        self.root_path = root_path

        self.cwd = root_path

        self.clients = dict()
        self.file_helper = FileHelper(self)
        self.http_helper = HttpHelper(self)

        # constant response headers
        self.const_headers = {"Server"}

    def start_listening(self):
        self.socket.bind((self.ipv4addr, self.port))
        self.socket.listen(1024)

    def build_response(self, request: HttpRequest) -> bytes:
        status, version, content, headers = self.http_helper.get_response_params(
            request
        )
        builder = HttpResponseBuilder(status, version, content, **headers)
        return builder.build("utf-8")

    async def start(self):
        self.server = await asyncio.start_server(
            self.serve_client, self.ipv4addr, self.port
        )
        logger.info(f"Now serving on http://{self.ipv4addr}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def serve_client(self, reader, writer):
        request = await reader.read(1024)
        logger.debug(f"Received request: {request.decode()}")
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

    HTML_500 = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>500 Internal Server Error</title>
            </head>
            <body>
                <h1>500 Internal Server Error</h1>
                <p>The server encountered an internal error and was unable to complete your request.</p>
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
        self.file_helper = self.server.file_helper
        self.allowed = allowed

    @staticmethod
    def erronous_status(status: http.HTTPStatus):
        return status.value >= 400

    def get_status(self, filereq_ctx, req: HttpRequest):
        if req.method.upper() not in self.allowed:
            return http.HTTPStatus.METHOD_NOT_ALLOWED
        elif not filereq_ctx.exists:
            return http.HTTPStatus.NOT_FOUND
        else:
            # default case
            return http.HTTPStatus.OK

    def get_response_params(self, req: HttpRequest):
        version = self.get_version()
        filereq_ctx = self.file_helper.get_filereq_ctx(req.uri)
        logger.debug(f"File request context: {filereq_ctx}")
        status = self.get_status(filereq_ctx, req)
        content = self.get_content(filereq_ctx, status)
        headers: dict = self.get_header_fields(filereq_ctx, status, content)
        
        return status, version, content, headers

    def get_version(self):
        return "HTTP/" + str(self.server.http_version)

    def handle_error_content(self, status):
        content = None
        if status is http.HTTPStatus.NOT_FOUND:
            content = self.HTML_404
        elif status is http.HTTPStatus.INTERNAL_SERVER_ERROR:
            content = self.HTML_500
        return content

    def get_fileserver_content(self, filepath):
        if self.file_helper.is_directory(filepath):
            listgen = HTMLListGenerator(self.file_helper.get_files_cwd())
            return listgen.construct_html_filelist()
        elif self.file_helper.is_file(filepath):
            return self.file_helper.get_file_content(filepath)

    def get_content(self, filereq_ctx, status):
        if self.erronous_status(status):
            return self.handle_error_content(status)
        return self.get_fileserver_content(filereq_ctx.filepath)

    def get_header_fields(self, filereq_ctx, status, content):
        fields = {}

        if content:
            fields["Content-Length"] = str(len(content))
            fields["Content-Type"] = self.get_mimetype(filereq_ctx)

        elif status is http.HTTPStatus.METHOD_NOT_ALLOWED:
            fields["Allow"] = ", ".join(self.allowed)

        return fields

    def get_mimetype(self, filereq_ctx):
        if filereq_ctx.dir_request:
            # html containing list of files
            return mimetypes.types_map['.html']
        return mimetypes.types_map[filereq_ctx.ext]


class HTMLListGenerator:
    def __init__(self, files: list):
        self.files = files

    def construct_html_filelist(self) -> str:
        htmllist = "<ul>"
        for entry in self.files:
            print(entry)
            pass
        return "list"
