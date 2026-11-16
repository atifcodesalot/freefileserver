
import os



class FileHelper:
    def __init__(self, server):
        self.server = server
        self.root = self.server.root_path
        
    def get_abs_path(self, path):
        abs_path = os.path.join(self.root, path)
        return abs_path
        
    def search_file(self, path):
        abs_path = self.get_abs_path(path)
        if not os.path.exists(abs_path):
            return False
        file = open(abs_path, "rb")
        return file
    
    def get_file_content(self, path):
        file = self.search_file(path)
        if not file:
            return None
        content = file.read()
        file.close()
        return content
    
    def get_file_ext(self, filename):
        # return the last split of .
        return '.' + filename.split('.')[-1]
    
    def get_files_cwd(self):
        cwd = self.server.cwd
        for ent in os.scandir(cwd):
            yield ent
            
    def is_directory(self, path):
        abs_path = self.get_abs_path(path)
        if not os.path.exists(abs_path):
            return False
        return os.path.isdir(abs_path)
    
    def is_file(self, path):
        abs_path = self.get_abs_path(path)
        if not os.path.exists(abs_path):
            return False
        return os.path.isfile(abs_path)
    
    
            
            
    