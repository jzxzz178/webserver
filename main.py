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
    s = Server('127.0.0.1', 53210, 'sourse1.com', '/web_site1')
    s.start()

    # TODO: чтобы создавалось столько серверов, сколько портов в конфиге
