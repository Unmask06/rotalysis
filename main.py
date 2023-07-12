from PyQt5 import QtWidgets , QtCore
import sys

from rotalysis import Core
from gui import MainWindow

class RedirectOutput:
    def __init__(self, printOccured):
        self.printOccured = open("text.txt", "w")

    def write(self, string):
        self.printOccured.write(string)

    def flush(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

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

    def print_to_output(message):
        window.lbOutput.setText(window.lbOutput.text() + message)


    def run():
        for key in widget.keys():
            set_path(key)
        print(paths)
        window.tabWidget.setCurrentIndex(1)
        window.ProgressBar.setValue(0)

        core = Core(*paths.values(),window = window)
        core.process_task()

        print_to_output(
            "Program finished successfully! \
            \nCheck the Error message and modify the input files accordingly and rerun the application."
        )
        window.ProgressBar.setValue(100)
        window.tabWidget.setCurrentIndex(1)


    window.show()

    window.pbRun.clicked.connect(run)

    sys.exit(app.exec_())
