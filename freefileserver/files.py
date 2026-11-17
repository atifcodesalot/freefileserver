import os
import urllib
from dataclasses import dataclass


@dataclass    
class FileReqCtx:
    exists: bool
    dir_request: bool
    filepath: str
    filename: str
    ext: str

class FileHelper:
    def __init__(self, server):
        self.server = server
        self.root = self.server.root_path

    def get_abs_path(self, path):
        if path.startswith('/'):
            # remove / from the start of the path
            # to avoid the legendary behaviour of:
            # os.path.join('.', '/path') == '/path'
            path = path[1:]
        abs_path = os.path.join(self.root, path)
        return abs_path

    def search_file(self, filepath):
        if not os.path.exists(filepath):
            return
        file = open(filepath, "rb")
        return file

    def get_file_content(self, filepath):
        file = self.search_file(filepath)
        if not file:
            return None
        content = file.read()
        file.close()
        return content

    def get_file_ext(self, filename):
        # return the last split of .
        return "." + filename.split(".")[-1]

    def get_files(self, filepath):
        return os.scandir(filepath)

    def is_directory(self, filepath):
        if not os.path.exists(filepath):
            return False
        return os.path.isdir(filepath)

    def is_file(self, filepath):
        if not os.path.exists(filepath):
            return False
        return os.path.isfile(filepath)

    # take an url path and return it to a readable file path
    def to_filepath(self, req_uri: str):
        parsed_url = urllib.parse.urlparse(req_uri)
        # decode uri first
        path = urllib.parse.unquote(parsed_url.path)
        # normalize
        normpath = os.path.normpath(path)
        
        return self.get_abs_path(normpath.replace("/", os.sep))

    def get_filename(self, filepath):
        return os.path.basename(filepath)
    
    def get_filereq_ctx(self, req_uri) -> FileReqCtx:
        filepath = self.to_filepath(req_uri)
        filename = self.get_filename(filepath)
        exists = os.path.exists(filepath)
        dir_request = self.is_directory(filepath)
        ext = self.get_file_ext(filename)
        if dir_request:
            ext = None
        return FileReqCtx(exists, dir_request, filepath, filename, ext)
            
