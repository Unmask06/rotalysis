import os
import sys


def get_app_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        return os.path.abspath(os.path.dirname(sys.argv[0]))
