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

logger = logging.getLogger('app.http_parser')


class HttpParser:
    def __init__(self, service_name, service_port, service_path, client_socket: socket, client_addr):
        self.service_name = service_name
        self.service_port = service_port
        self.service_path = service_path
        self.client_socket = client_socket
        self.client_addr = client_addr

    def parse_request(self):
        rfile = self.client_socket.recv(2048).decode('iso-8859-1')

        method, target, ver = self.parse_request_line(rfile)
        logger.debug(f'{method} {target} {ver}')

        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        logger.debug(f'Host: {host}')
        if not host:
            logger.warning('Bad request')
        hdrs_str = 'Headers are: '
        for i in range(len(headers.keys())):
            hdrs_str += f'[{headers.keys()[i]}: {headers.values()[i]}]'
        logger.debug(hdrs_str)
        body_idx = rfile.find(headers.values()[-1]) + len(headers.values()[-1])

        body = self.parse_body(rfile, body_idx)
        logger.debug(f'Body is: {body}')

        return Request(method, target, ver, headers, body)

    def rfile_to_str(self, rfile: io.BufferedReader):
        content = b''
        for line in rfile:
            content += line
            break
        content = content.decode('iso-8859-1')
        return content

    def parse_body(self, rfile: str, body_idx: int):
        raw = rfile[body_idx:]
        body_line = raw.strip('\n')
        for i in range(3):
            body_line = raw.strip('\n')
        return body_line

    def parse_headers(self, rfile: str):
        MAX_HEADERS = 100
        headers = []
        raw = rfile.split('\n')[1:]
        for line in raw:
            if len(line) > MAX_LINE:
                logger.warning(f'Header line is too long from user {self.client_addr}')

            if line in (b'\r\n', b'\n', b''):
                # завершаем чтение заголовков
                break

            headers.append(line + '\n')
            if len(headers) > MAX_HEADERS:
                logger.warning(f'Too many headers from user {self.client_addr}')

        sheaders = ''.join(headers)
        return Parser().parsestr(sheaders)

    def parse_request_line(self, rfile: str):
        global MAX_LINE  # используется в нескольких методах
        req_line = rfile.split('\n')[0]
        if len(req_line) > MAX_LINE:
            logger.warning(f'Request line is too long from user {self.client_addr}')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            logger.warning(f'Malformed request line from user {self.client_addr}')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            logger.warning(f'Unexpected HTTP version from user {self.client_addr}')

        return method, target, ver

    def handle_request(self, request: Request):
        curr_dir = pathlib.Path.cwd()
        path = str(curr_dir).replace('\\', '/') + self.service_path + request.path
        logger.debug(f'Got path: {path}')

        if request.method == 'GET':
            if not os.path.exists(path) or not os.path.isfile(path):
                self.send_response(Response(400, 'Bad request'))
                logger.info(f'400 Bad request from user {self.client_addr}')
                return
            file = self.read_bytes_from_file(path)
            r = self.send_response(Response(200, 'OK', body=file))
            return

        if request.method == 'POST':
            if os.path.isfile(path):
                self.send_response(Response(400, 'Bad request',
                                            body=f'File with specified name "{request.path}" already exists'))
                logger.info(f'400 Bad request from user {self.client_addr}')
                return
            try:
                file = open(path, 'w')
                file.write(request.body)
                file.close()
                self.send_response(Response(200, 'OK', body=f'File {request.path} succesfully created'))
            except Exception as e:
                # raise e
                if file:
                    os.remove(path)
                self.send_error(Response(400, 'Bad request', body=f'{e}'), e)
                logger.warning(f'400 Bad request from user {self.client_addr}')
            finally:
                if file:
                    file.close()

        self.send_response(Response(400, 'Bad request'))
        logger.warning(f'400 Bad request from user {self.client_addr}')

    def send_response(self, response: Response):
        logger.debug(f'{response.status}: {response.reason}')
        status_line = bytes(f'HTTP/1.1 {response.status} {response.reason}', 'iso-8859-1')
        r = status_line + b'\r\n'
        hdrs = b''
        if response.headers:
            for k, v in response.headers:
                header_line = f'{k}: {v}\r\n'
                hdrs += (header_line.encode('iso-8859-1'))
        hdrs += b'\r\n'
        r += hdrs
        if response.body:
            r += str(response.body).encode('iso-8859-1')
        self.client_socket.sendall(r)
        return r

    def send_error(self, error: Response, e=None):
        if e:
            logger.warning(e)
        try:
            status = error.status
            reason = error.reason
            body = error.body.encode('utf-8')
        except Exception as ex:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'
            logger.warning(f'Internal server error for user {self.client_addr}')
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
