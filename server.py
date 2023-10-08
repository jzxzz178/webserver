import socket
import threading
from http_parser import HttpParser
from response import Response


class Server(threading.Thread):
    def __init__(self, host: str, port: int, service_name: str, service_path: str):
        threading.Thread.__init__(self, name=service_name)
        self.host = host
        self.port = port
        self.service_name = service_name
        self.service_path = service_path

        # TODO: СДЕЛАТЬ ПОТОКОБЕЗОПАСНЫМ
        # self.parser = HttpParser(service_name, port, service_path)

        print(f'service {service_name} started and handling on {self.host}:{self.port}')

    def run(self):
        server_socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM,
                                      proto=0)
        try:
            server_socket.bind((str(self.host), int(self.port)))
            server_socket.listen()
            while True:
                client_sock, client_addr = server_socket.accept()
                print('Client', client_addr, f' connected to {self.service_name} on port {self.port}')
                # data = client_sock.recv(1024)
                # if not data:
                #     print('Клиент отключился')
                #     break
                try:
                    # self.serve_client(client_sock, client_addr)
                    th = threading.Thread(target=self.serve_client,
                                          name=client_addr,
                                          args=(client_sock, client_addr),
                                          daemon=False)
                    th.start()
                    # th.join()
                except Exception as e:
                    # client_sock.sendall(bytes(e))
                    print(e)
                # finally:
                #     print('Клиент отключился')

        finally:
            print('finally part')
            server_socket.close()

    def serve_client(self, conn: socket, addr):
        parser = HttpParser(self.service_name, self.port, self.service_path, conn)
        # parser.start()
        try:
            print(f'Started serving client {addr}')
            request = parser.parse_request()
            # print('Parsed incoming request')
            resp = parser.handle_request(request)
            # parser.send_response(resp)
            conn.close()
            print(f'client {addr} served')
        except ConnectionResetError:
            conn.close()
        except Exception as e:
            parser.send_error(Response(400, 'Bad request'), e)
