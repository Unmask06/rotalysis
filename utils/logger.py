import logging
import os

# TODO: improve clean log file function and delete log file function


class Logger:
    def __init__(self, name="log", path=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="{asctime}: {levelname}: {message}", datefmt="%d-%m-%Y %H:%M:%S", style="{"
        )

        if path is None:
            path = os.getcwd()
        log_file = os.path.join(path, f"{name}.log")
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        self.file_handler.close()

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def debug(self, message):
        self.logger.debug(message)

    def clean_log_file(self):
        open(self.file_handler.baseFilename, "w")
        self.file_handler.close()

    def delete_log_file(self):
        self.file_handler.close()
        self.logger.removeHandler(self.file_handler)
        os.remove(self.file_handler.baseFilename)
