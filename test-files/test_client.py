import pathlib
import socket

if __name__ == '__main__':

    # print(pathlib.Path.cwd() / 'hh')
    # Создаем сокет
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Устанавливаем хост и порт для подключения
    server_host = '127.0.0.1'
    server_port = 53210

    # Подключаемся к серверу
    client_socket.connect((server_host, server_port))

    # Создаем объект файла на основе сокета
    client_file = client_socket.makefile('rwb', buffering=0,
                                         encoding='iso-8859-1')  # 'rw' - режим чтения и записи, buffering=1 - буферизация

    # Отправляем запрос на сервер
    request = b"GET /files/test.txt HTTP/1.1\r\nHost: sourse1.com\r\n\r\n"
    client_socket.sendall(request)
    # client_file.write(request)
    # client_file.flush()  # Сбрасываем буфер

    # Читаем ответ от сервера

    # response = b""
    # counter = 0
    # while True:
    #     data = client_socket.recv(1024)  # Читаем до 1024 байт данных
    #     counter += 1
    #     if not data or counter > 20:
    #         client_socket.close()
    #         break
    #     response += data

    data = client_socket.recv(1024)  # Читаем до 1024 байт данных
    print(data.decode('iso-8859-1'))

    # Закрываем соединение и сокет
    client_file.close()
    client_socket.close()
