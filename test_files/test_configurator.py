import os
from client_core import Client
import configparser

if __name__ == '__main__':
    os.chdir('../')
    config = configparser.ConfigParser()
    config.read('config.ini')
    for name in config.sections():
        print(config[name]['host'], int(config[name]['port']))
        client = Client(config[name]['host'],
                        int(config[name]['port']))
        client.start()
        break
    print()
