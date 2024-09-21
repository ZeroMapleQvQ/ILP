import logging
import os


class Logger:
    def __init__(self, filepath=None):
        # filename = "C:\\log.txt"
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "log.txt")
        logging.basicConfig(
            level=logging.DEBUG,
            filename=filepath,
            filemode="a",
            format="[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s",
            encoding="utf-8",
        )
        self.logger = logging.getLogger()

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)
