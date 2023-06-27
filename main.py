from PyQt5 import QtWidgets
import sys

from rotalysis import Core
from gui import MainWindow

def get_config_path():
    config_path = window.tbox_config.toPlainText()
    print(config_path)

def get_input_path():
    input_path = window.tbox_InputFolder.toPlainText()
    print(input_path)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    window.bbConfig.accepted.connect(get_config_path)
    window.bbInputFolder.accepted.connect(get_input_path)

    

    # core = Core(config_path, task_path, errmsg_path, input_path, output_path)
    # core.intialize()
    # core.process_task()

    # print(
    #     "Program finished successfully! \
    #     \nCheck the Error message and modify the input files accordingly and rerun the application."
    # )
    # close_program = questionary.confirm("Do you want to close the program?").ask()
    # if close_program:
    #     print("Closing the program...")
    # else:
    #     input("Press Enter to close the program...")
    
    sys.exit(app.exec_())
