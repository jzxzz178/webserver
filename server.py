import socket
import threading
from http_parser import HttpParser
from response import Response
import logging

logger = logging.getLogger('app.server')


class Server(threading.Thread):
    def __init__(self, host: str, port: int, service_name: str, service_path: str):
        threading.Thread.__init__(self, name=service_name)
        self.host = host
        self.port = port
        self.service_name = service_name
        self.service_path = service_path
        logger.debug(f'service {service_name} started and handling on {self.host}:{self.port}')

    def run(self):
        server_socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM,
                                      proto=0)
        client_addr = ''
        try:
            server_socket.bind((str(self.host), int(self.port)))
            server_socket.listen()
            while True:
                client_sock, client_addr = server_socket.accept()
                logger.info(f'Client {client_addr} connected to {self.service_name} on port {self.port}')
                try:
                    th = threading.Thread(target=self.serve_client,
                                          name=client_addr,
                                          args=(client_sock, client_addr),
                                          daemon=False)
                    th.start()
                except Exception as e:
                    logger.warning(e)

        finally:
            logger.warning(f'Client {client_addr or "none_addr"} disconnected')
            server_socket.close()

    def serve_client(self, conn: socket, addr):
        parser = HttpParser(self.service_name, self.port, self.service_path, conn, addr)
        logger.debug(f'Started serving client {addr}')
        request = parser.parse_request()
        parser.handle_request(request)
        logger.debug(f'client {addr} served')
        conn.close()
