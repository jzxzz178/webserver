import pathlib
import socket


def go():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_host = '127.0.0.1'
    server_port = 2100

    client_socket.connect((server_host, server_port))

    # Создаем объект файла на основе сокета
    client_file = client_socket.makefile('rwb', buffering=0,
                                         encoding='iso-8859-1')

    request = b"GET /files/test.txt HTTP/1.1\r\nHost: sourse1.com\r\n\r\n"
    client_socket.sendall(request)
    # client_file.write(request)
    # client_file.flush()  # Сбрасываем буфер

    data = client_socket.recv(1024)  # Читаем до 1024 байт данных
    print(data.decode('iso-8859-1') + '\r\n\r\n')

    # Закрываем соединение и сокет
    client_file.close()
    client_socket.close()
