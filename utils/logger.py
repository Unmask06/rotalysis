import logging
import os


class Logger:
    def __init__(self, name="log", path=os.getcwd()):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="{asctime}: {levelname}: {message}", datefmt="%d-%m-%Y %H:%M:%S", style="{"
        )

        log_file = os.path.join(path, f"{name}.log")
        self.file_handler = None
        handlers = self.logger.handlers

        # Check if a FileHandler already exists
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                self.file_handler = handler
            elif isinstance(handler, logging.StreamHandler):
                self.stream_handler = handler
                break

        if not self.file_handler:
            self.file_handler = logging.FileHandler(log_file, mode="a")
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

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
