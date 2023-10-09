import socket
import threading


class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.server_host = host
        self.server_port = port

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))

        client_file = client_socket.makefile('rwb', buffering=0, encoding='iso-8859-1')
        request = b"GET /files/test.txt HTTP/1.1\r\nHost: sourse1.com\r\n\r\n"

        client_file.write(request)
        client_file.flush()

        # client_socket.sendall(request)
        # data = client_file.read()

        data = client_socket.recv(1024).decode('iso-8859-1')
        data = data.replace('\r\n\r\n', '\r\n...\r\n...')
        print(data + '\r\n')

        client_file.close()
        client_socket.close()
