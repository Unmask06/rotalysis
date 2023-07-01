from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QDialogButtonBox,
    QPushButton,
    QPlainTextEdit,
)
from PyQt5 import uic


# load test.ui file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/main_window.ui", self)
        self.set_default_values()

        self.connect_buttons()

    def set_default_values(self):
        default_values = {
            "tbox_config": "Config.xlsx",
            "tbox_tasklist": "TaskList.xlsx",
            "tbox_InputFolder": "/Input",
            "tbox_OutputFolder": "/Output",
        }

        for widget_name, default_value in default_values.items():
            widget = self.findChild(QPlainTextEdit, widget_name)
            widget.setPlainText(default_value)
    
    def connect_buttons(self):
        buttons = {
            "pbConfig": {"dialog": QFileDialog.getOpenFileName, "widget": "tbox_config"},
            "pbTaskList": {"dialog": QFileDialog.getOpenFileName, "widget": "tbox_tasklist"},
            "pbInputFolder": {
                "dialog": QFileDialog.getExistingDirectory,
                "widget": "tbox_InputFolder",
            },
            "pbOutputFolder": {
                "dialog": QFileDialog.getExistingDirectory,
                "widget": "tbox_OutputFolder",
            },
        }

        for button_name, button_info in buttons.items():
            try:
                button = self.findChild(QPushButton, button_name)
                widget_name = button_info["widget"]
                widget = self.findChild(QPlainTextEdit, widget_name)
                dialog_func = button_info["dialog"]

                button.clicked.connect(
                    lambda _, btn=button, dlg=dialog_func, wgt=widget: self.handle_button_click(
                        btn, dlg, wgt
                    )
                )
            except Exception as e:
                print(e, button_name)

    def handle_button_click(self, button, dialog_func, widget):
        options = QFileDialog.Options()
        if dialog_func == QFileDialog.getOpenFileName:
            file_path, _ = dialog_func(
                self,
                caption=button.text(),
                options=options,
                filter="Excel Files (*.xlsx)",
                directory="",
            )
            if file_path:
                widget.setPlainText(file_path)
        elif dialog_func == QFileDialog.getExistingDirectory:
            folder_path = dialog_func(self, caption=button.text(), options=options, directory="")
            if folder_path:
                widget.setPlainText(folder_path)
