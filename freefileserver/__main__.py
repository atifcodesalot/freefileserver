

from .server import FileHttpServer
import sys

HTTPS_FLAG = "--secure"

def main():
    root = '.'
    _ssl = False
    if len(sys.argv) > 1:
        if sys.argv[-1] != HTTPS_FLAG:
            root = sys.argv[-1]
    if HTTPS_FLAG in sys.argv:
        _ssl = True
    server = FileHttpServer("0.0.0.0", 8008, root, _ssl=_ssl)
    server.run()

if __name__ == "__main__":
    main()