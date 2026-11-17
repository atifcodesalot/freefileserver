

from .server import FileHttpServer
import sys


def main():
    root = '.'
    if len(sys.argv) > 1:
        root = sys.argv[-1]
    server = FileHttpServer("0.0.0.0", 8008, root)
    server.run()

if __name__ == "__main__":
    main()