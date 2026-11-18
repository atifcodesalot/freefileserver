from sys import exception

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

        self.file_helper = FileHelper(self)
        self.http_helper = HttpHelper(self)

        # constant response headers
        self.const_headers = {"Server": "FreeFileServer", "Cache-Control": "no-store"}

    def handle_internal_error(self):
        status = http.HTTPStatus.INTERNAL_SERVER_ERROR
        content = "INTERNAL SERVER ERROR"
        headers = {
            "Content-Length": str(len(content)),
            "Content-Type": mimetypes.types_map[".html"],
        }
        version = "HTTP/1.1"
        return status, version, content, headers

    def build_response(self, request: HttpRequest) -> bytes:
        try:
            status, version, content, headers = self.http_helper.get_response_params(
                request
            )
        except:
            logger.error("An internal error occurred while processing the request.")
            status, version, content, headers = self.handle_internal_error()
        headers.update(self.const_headers)
        builder = HttpResponseBuilder(status, version, content, **headers)
        return builder.build("utf-8")

    async def start(self):
        self.server = await asyncio.start_server(
            self.serve_client, self.ipv4addr, self.port
        )
        logger.info(f"Now serving on http://{self.ipv4addr}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def serve_exchange(self, reader, writer):
        request = await reader.read(1024)
        logger.debug(f"Received request: {request.decode()}")
        if request == b"":
            return None
        reqobj = HttpRequest(request.decode())
        response = self.build_response(reqobj)
        writer.write(response)
        await writer.drain()
        return reqobj

    async def serve_client(self, reader, writer):
        reqobj = await self.serve_exchange(reader, writer)
        if not reqobj:
            await self.end_client_conn(writer)
            return
        await writer.drain()
        if not reqobj.invalid and reqobj.Connection == "keep-alive":
            while await self.serve_exchange(reader, writer):
                continue

        await self.end_client_conn(writer)

    async def end_client_conn(self, client_writer):
        logger.debug(
            f"Ending client connection with writer: {client_writer.get_extra_info('peername')}"
        )
        client_writer.close()
        await client_writer.wait_closed()

    def run(self):
        asyncio.run(self.start(), debug=False)


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
    HTML_401 = lambda resource: f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>401 Unauthorized</title>
            </head>
            <body>
                <h1>401 Unauthorized</h1>
                <p>You are not authorized to access {resource}</p>
            </body>
            </html>
    """

    HTML_400 = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>400 Bad Request</title>
            </head>
            <body>
                <h1>400 Bad Request</h1>
                <p>The server could not understand your request due to invalid syntax.</p>
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
        if req.invalid:
            return http.HTTPStatus.BAD_REQUEST
        elif req.method.upper() not in self.allowed:
            return http.HTTPStatus.METHOD_NOT_ALLOWED
        elif not filereq_ctx.exists:
            return http.HTTPStatus.NOT_FOUND
        elif not filereq_ctx.authorized:
            return http.HTTPStatus.UNAUTHORIZED
        else:
            # default case
            return http.HTTPStatus.OK

    def get_response_params(self, req: HttpRequest):
        version = self.get_version()
        filereq_ctx = (
            self.file_helper.get_filereq_ctx(req.uri) if not req.invalid else None
        )
        if filereq_ctx:
            logger.debug(f"File request uri: {req.uri}")
            logger.debug(f"File request context: {filereq_ctx}")
        status = self.get_status(filereq_ctx, req)
        content = self.get_content(filereq_ctx, status)
        headers: dict = self.get_header_fields(filereq_ctx, status, content)

        return status, version, content, headers

    def get_version(self):
        return "HTTP/" + str(self.server.http_version)

    def handle_error_content(self, filereq_ctx, status):
        content = None
        if status is http.HTTPStatus.NOT_FOUND:
            content = self.HTML_404
        elif status is http.HTTPStatus.UNAUTHORIZED:
            content = self.__class__.HTML_401(filereq_ctx.filepath)
        elif status is http.HTTPStatus.BAD_REQUEST:
            content = self.HTML_400
        return content

    def get_fileserver_content(self, filepath):
        if self.file_helper.is_directory(filepath):
            listgen = HTMLListGenerator(filepath, self.file_helper.get_files(filepath))
            return listgen.construct()
        elif self.file_helper.is_file(filepath):
            return self.file_helper.get_file_content(filepath)

    def get_content(self, filereq_ctx, status):
        if self.erronous_status(status):
            return self.handle_error_content(filereq_ctx, status)
        return self.get_fileserver_content(filereq_ctx.filepath)

    def get_header_fields(self, filereq_ctx, status, content):
        fields = {}

        if content:
            fields["Content-Length"] = str(len(content))

            if self.erronous_status(status):
                fields["Content-Type"] = mimetypes.types_map[".html"]
            else:
                fields["Content-Type"] = self.get_mimetype(filereq_ctx)
                if not filereq_ctx.dir_request:
                    fields["Content-Disposition"] = f'inline; filename="{filereq_ctx.filename}"'

        if status is http.HTTPStatus.METHOD_NOT_ALLOWED:
            fields["Allow"] = ", ".join(self.allowed)

        return fields

    def get_mimetype(self, filereq_ctx):
        if filereq_ctx.dir_request:
            # html containing list of files
            return mimetypes.types_map[".html"]
        return mimetypes.types_map.get(filereq_ctx.ext, "text/plain")


class HTMLListGenerator:
    def __init__(self, parent, files: list):
        self.parent = parent
        self.files = list(files)
        self.empty = not bool(self.files)

    def construct_list_element(self, file_entry):
        li_html = "<li>"
        li_html += f'<a href="{file_entry.name}/">{file_entry.name}{"/" if file_entry.is_dir() else ""}</a>'
        if file_entry.is_dir():
            li_html += " &#128193; &#x21A9;"
        else:
            li_html += " &#128196;"
        li_html += "</li>"

        return li_html

    def construct_html_filelist(self) -> str:
        header = (
            f"<h style='font-size: 24px;'> Directory listing for {self.parent} </h>"
        )
        if not self.empty:
            html_list = header + "<body> <ul>"
            for entry in self.files:
                html_list += self.construct_list_element(entry)
            html_list += "</body></ul>"
        else:
            html_list = header + "<ul> looks like this directory is empty. </ul>"
        return html_list

    def construct(self):
        start = "<!DOCTYPE html> <html style='font-family: Arial, sans-serif;'>"
        start += '\n <head><meta charset="UTF-8"></head>'
        end = "</html>"
        return start + self.construct_html_filelist() + end
