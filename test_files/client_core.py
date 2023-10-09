import socket
import threading


class Client(threading.Thread):
    def __init__(self, host, port, file_name='text1', text='This is the body of request!!!'):
        threading.Thread.__init__(self)
        self.server_host = host
        self.server_port = port
        self.file_name = file_name
        self.text = text

        self.client_socket = None
        self.client_file = None

    def run(self):
        self.open_connection()
        self.make_post_request()
        self.close_connection()

        self.open_connection()
        self.make_get_request()
        self.close_connection()

    def open_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_host, self.server_port))
        self.client_file = self.client_socket.makefile('rwb', buffering=0, encoding='iso-8859-1')

    def close_connection(self):
        self.client_file.close()
        self.client_socket.close()

    def make_post_request(self):
        request = (
            bytes(
                f"POST /files/{self.file_name}.txt HTTP/1.1\r\n"
                f"Host: sourse1.com\nContent-Type: text/html; charset=utf-8\n\n"
                f"{self.text}\n\n", 'iso-8859-1'))

        # client_socket.sendall(request)
        self.client_file.write(request)
        self.client_file.flush()

        data = self.client_socket.recv(1024).decode('iso-8859-1')
        # data = client_file.read()
        data = data.replace('\r\n\r\n', '\r\n...\r\n...\r\n')
        print(data + '\r\n')

    def make_get_request(self):
        request = bytes(
            f"GET /files/{self.file_name}.txt HTTP/1.1\r\n"
            f"Host: sourse1.com\nContent-Type: text/html; charset=utf-8\n\n", 'iso-8859-1')

        # client_socket.sendall(request)
        self.client_file.write(request)
        self.client_file.flush()

        data = self.client_socket.recv(1024).decode('iso-8859-1')
        # data = client_file.read()
        data = data.replace('\r\n\r\n', '\r\n...\r\n...\r\n')
        print(data + '\r\n')
