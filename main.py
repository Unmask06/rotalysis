from PyQt5 import QtWidgets
from gui import Ui_MainWindow



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated .py file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect the button's clicked signal to a custom slot
        self.ui.button1.clicked.connect(self.print_hello)

    def print_hello(self):
        print("Hello World")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
