from socket import socket
from email.parser import Parser

import Request

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class HttpParser:
    def parse_request(self, conn: socket):
        global MAX_LINE
        rfile = conn.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        if not host:
            raise Exception('Bad request')
        if host not in (self._server_name,
                        f'{self._server_name}:{self._port}'):
            raise Exception('Not found')
        return Request(method, target, ver, rfile)

    def parse_headers(self, rfile):
        global MAX_HEADERS
        headers = []
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                # завершаем чтение заголовков
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise Exception('Too many headers')

        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def parse_request_line(self, rfile):
        raw = rfile.readline(MAX_LINE + 1)  # эффективно читаем строку целиком
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()  # разделяем по пробелу
        if len(words) != 3:  # и ожидаем ровно 3 части
            raise Exception('Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')

        return method, target, ver

    def handle_request(self, req):
        pass  # TODO: implement me

    def send_response(self, conn, resp):
        pass  # TODO: implement me

    def send_error(self, conn, err):
        pass  # TODO: implement me
