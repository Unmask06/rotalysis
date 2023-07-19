import sys
import time

from PyQt6 import QtCore, QtWidgets

from gui import MainWindow, SplashScreen
from rotalysis import Core


class RedirectOutput:
    def __init__(self, printOccured):
        self.printOccured = open("text.txt", "w")

    def write(self, string):
        self.printOccured.write(string)

    def flush(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = MainWindow()
    splash_screen = SplashScreen()
    splash_screen.show()
    time.sleep(5)
    splash_screen.finish(window)

    widget = {
        "Config": window.tbox_config,
        "InputFolder": window.tbox_InputFolder,
        "OutputFolder": window.tbox_OutputFolder,
        "TaskList": window.tbox_tasklist,
    }

    paths = {"Config": "", "TaskList": "", "InputFolder": "", "OutputFolder": ""}

    def get_path(field, text_box_dict=widget):
        for key, widget in text_box_dict.items():
            if field == key:
                path = widget.toPlainText()
                return path

    def set_path(field):
        paths[field] = get_path(field)


    def run():
        for key in widget.keys():
            set_path(key)
        print(paths)

        core = Core(*paths.values(), window=window)
        core.process_task()

        window.ProgressBar.setValue(100)

    window.show()

    window.pbRun.clicked.connect(run)

    sys.exit(app.exec())
