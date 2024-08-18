import logging
import os


class Logger:
    def __init__(self, filepath):
        # filename = "C:\\log.txt"
        if filepath == None:
            filepath = os.path.join(os.path.dirname(__file__), 'log.txt')
        logging.basicConfig(level=logging.DEBUG, filename=filepath, filemode='a',
                            format='[%(levelname)s][%(asctime)s]: %(message)s')
        self.logger = logging.getLogger()

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)
