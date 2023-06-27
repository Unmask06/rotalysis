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

        # Connect the button's clicked signal to a custom slot
        self.pbConfig = self.findChild(QPushButton, "pbConfig")
        self.tbox_config = self.findChild(QPlainTextEdit, "tbox_config")
        self.pbConfig.clicked.connect(self.open_file_dialog)

        self.pbInputFolder = self.findChild(QPushButton, "pbInputFolder")
        self.tbox_InputFolder = self.findChild(QPlainTextEdit, "tbox_InputFolder")
        self.pbInputFolder.clicked.connect(self.open_folder_dialog)

    def modify_button(self):
        self.button.setText("Modified Button")
        self.button.setEnabled(False)

    def print_hello(self):
        print("Hello World")
        self.button.setEnabled(True)
        self.modify_button()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options
        )
        if file_path:
            self.tbox_config.setPlainText(file_path)

    def open_folder_dialog(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", options=options)
        if folder_path:
            self.tbox_InputFolder.setPlainText(folder_path)
