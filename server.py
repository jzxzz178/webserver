import socket
import threading
from http_parser import HttpParser


class Server(threading.Thread):
    def __init__(self, host, port, name):
        threading.Thread.__init__(self, name=name)
        self.host = host
        self.port = port
        self.name = name
        self.parser = HttpParser()
        print(f'{name} started')

    def run(self):
        server_socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM,
                                      proto=0)
        try:
            server_socket.bind((str(self.host), int(self.port)))
            server_socket.listen()
            while True:
                client_sock, client_addr = server_socket.accept()
                print('Connected by', client_addr)
                print(self.name)
                data = client_sock.recv(1024)
                if not data:
                    print('Клиент отключился')
                    break
                try:
                    self.serve_client(client_sock, client_addr)
                except Exception as e:
                    # client_sock.sendall(bytes(e))
                    print(e)

        finally:
            server_socket.close()

    def serve_client(self, conn, addr):
        try:
            print(f'Started serve client {addr}')
            req = self.parser.parse_request(conn)
            resp = self.parser.handle_request(req)
            self.parser.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            self.parser.send_error(conn, e)
