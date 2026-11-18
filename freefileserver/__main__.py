

from .server import FileHttpServer
import sys


def main():
    root = '.'
    _ssl = False
    if len(sys.argv) > 1:
        root = sys.argv[-1]
    if "--https" in sys.argv:
        _ssl = True
    server = FileHttpServer("0.0.0.0", 8008, root, _ssl=_ssl)
    server.run()

if __name__ == "__main__":
    main()