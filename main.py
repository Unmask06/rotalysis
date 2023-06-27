from PyQt5 import QtWidgets
import sys

from rotalysis import Core
from gui import MainWindow

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

    def run():
        for key in widget.keys():
            set_path(key)
        print(paths)
        core = Core(*paths.values())
        core.intialize()
        core.process_task()

        print(
            "Program finished successfully! \
            \nCheck the Error message and modify the input files accordingly and rerun the application."
        )


    window.show()

    window.pbRun.clicked.connect(run)

    sys.exit(app.exec_())
