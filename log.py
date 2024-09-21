import logging
import os


class Logger:
    @classmethod
    def get_logger(cls, filepath=None, log_level=logging.INFO):
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "log.txt")
        logging.basicConfig(
            level=log_level,
            filename=filepath,
            filemode="a",
            format="[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s",
            encoding="utf-8",
        )
        return logging.getLogger()

    @classmethod
    def debug(cls, msg):
        cls.get_logger().debug(msg)

    @classmethod
    def info(cls, msg):
        cls.get_logger().info(msg)

    @classmethod
    def warning(cls, msg):
        cls.get_logger().warning(msg)

    @classmethod
    def error(cls, msg):
        cls.get_logger().error(msg)
