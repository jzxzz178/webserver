import configparser
import sys

from server import Server
import logging
import logging.handlers


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s'
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(filename="webserver_log.log", mode='w')
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.debug("Logger was initialized")


init_logger("app")
logger = logging.getLogger("app.main")

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    for name in config.sections():
        server = Server(config[name]['host'],
                        int(config[name]['port']),
                        config[name]['service_name'],
                        config[name]['service_path'])
        server.start()
