import socket
import threading


class Server(threading.Thread):
    def __init__(self, host, port, name):
        threading.Thread.__init__(self, name=name)
        self.host = host
        self.port = port
        self.name = name
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
                client_sock.sendall(data + bytes('; Who are you?', 'utf-8'))

        finally:
            server_socket.close()
