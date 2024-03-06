import logging
import os

log_file = "rotalysis"

logger = logging.getLogger(log_file)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="{asctime}: {levelname}: {message}", datefmt="%d-%m-%Y %H:%M:%S", style="{"
)
# addd file handler
file_handler = logging.FileHandler(log_file + ".log", mode="a")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# add ch handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


