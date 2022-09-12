from concurrent.futures import ThreadPoolExecutor
import socket

class BaseServer:

    def __init__(self, host, port, num_threads):
        self.host = host
        self.port = port
        self.num_threads = num_threads

    def start(self, serve_function):
        with ThreadPoolExecutor(max_workers=5) as executor:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind((self.host, self.port))
                server.listen()
                print(f"server listening on {(self.host, self.port)}")
                while True:
                    conn, addr = server.accept()
                    executor.submit(serve_function, conn, addr)
        print("server shutting down")