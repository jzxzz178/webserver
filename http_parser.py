import io
import os
import pathlib
from email.parser import Parser
from functools import lru_cache
from socket import socket
import logging

from request import Request
from response import Response

MAX_LINE = 64 * 1024
MAX_HEADERS = 100

logger = logging.getLogger('app.http_parser')


class HttpParser:
    def __init__(self, service_name, service_port, service_path, client_socket: socket):
        self.service_name = service_name
        self.service_port = service_port
        self.service_path = service_path
        self.client_socket = client_socket

    def parse_request(self):
        global MAX_LINE
        rfile = self.client_socket.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        logger.debug(f'{method} {target} {ver}')
        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        logger.debug(f'Host: {host}')
        if not host:
            raise Exception('Bad request')

        # if host not in (self.service_name, f'{self.service_name}:{self.service_port}'):
        #     raise Exception('Not found')

        return Request(method, target, ver, headers, rfile)

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

    def parse_request_line(self, rfile: io.BufferedReader):
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')
        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')

        return method, target, ver

    def handle_request(self, request: Request):
        curr_dir = pathlib.Path.cwd()
        path = str(curr_dir).replace('\\', '/') + self.service_path + request.path
        logger.debug(f'Got path: {path}')
        if not os.path.exists(path) or not os.path.isfile(path):
            (self.send_response(Response(400, 'Bad request')))
            return
        if request.method == 'GET':
            file = self.read_bytes_from_file(path)
            r = self.send_ok_response(file)

    def send_response(self, response, body=None):
        logger.debug(f'{response.status}: {response.reason}')
        status_line = bytes(f'HTTP/1.1 {response.status} {response.reason}')
        r = status_line
        if body:
            r = status_line + b'\r\n' + body
        self.client_socket.sendall(r.encode('iso-8859-1'))
        return r

        # wfile = self.client_socket.makefile('wb')
        # wfile.write(status_line.encode('iso-8859-1'))

        # if response.headers:
        #     for k, v in response.headers:
        #         header_line = f'{k}: {v}\r\n'
        #         wfile.write(header_line.encode('iso-8859-1'))
        # wfile.write(b'\r\n')
        # if response.body:
        #     wfile.write(response.body)
        #
        # wfile.flush()
        # wfile.close()

    def send_ok_response(self, body=None):
        logger.debug(f'{200}: OK')
        status_line = b'HTTP/1.1 200 OK'
        r = status_line
        if body:
            r = status_line + b'\r\n' + body
        self.client_socket.sendall(r)
        # wfile = self.client_socket.makefile('wb')
        # self.client_socket.send(status_line.encode('iso-8859-1'))
        # wfile.write(status_line.encode('iso-8859-1'))
        # wfile.flush()
        # wfile.close()
        return r

    def send_error(self, error: Response, e=None):
        if e:
            logger.warning(e)
        try:
            status = error.status
            reason = error.reason
            body = error.body.encode('utf-8')
        except:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'
        finally:
            response = Response(status, reason, [('Content-Length', len(body))], body)
            self.send_response(response)

    @lru_cache(maxsize=30)
    def read_bytes_from_file(self, path):
        file_to_bytes = b'\r\n'
        f = open(path, "rb")
        current_bytes = f.read(1024)
        while current_bytes:
            file_to_bytes += current_bytes
            current_bytes = f.read(1024)
        f.close()
        return file_to_bytes
