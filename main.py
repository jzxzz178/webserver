from server import Server

if __name__ == '__main__':
    s = Server('127.0.0.1', 53210, 'web_site1', '/web_site1')
    s.start()

    # TODO: чтобы создавалось столько серверов, сколько портов в конфиге
