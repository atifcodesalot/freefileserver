

from .server import FileHttpServer


def main():
    server = FileHttpServer("localhost", 8000, '.')
    server.run()

if __name__ == "__main__":
    main()