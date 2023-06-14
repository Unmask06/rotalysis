import questionary
from questionary import Style
from tqdm import tqdm
from art import text2art
import time
import os
from core import Core


# ANSI escape code for colors
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"


def animate_logo():
    company_name = "Tebodin"
    client_name = "ADNOC"
    program_name = "DECARB"
    clear_terminal()  # Optional: Clear the terminal screen before each frame
    print(RED + text2art(company_name) + RESET)
    time.sleep(1)
    clear_terminal()  # Optional: Clear the terminal screen before each frame
    print(BLUE + text2art(client_name) + RESET)
    time.sleep(1)
    clear_terminal()  # Optional: Clear the terminal screen before each frame
    print(GREEN + text2art(program_name) + RESET)
    time.sleep(1)
    clear_terminal()  # Optional: Clear the terminal screen before each frame


def clear_terminal():
    # Clear the terminal screen (for Unix-like systems)
    print("\033c", end="")


def is_valid_file_path(path):
    return os.path.isfile(path)


def is_valid_dir_path(path):
    return os.path.isdir(path)


def main():
    animate_logo()
    custom_style = Style(
        [
            ("qmark", "fg:blue bold"),
            ("question", "bold"),
            ("answer", "fg:green"),
            ("highlighted", "fg:black bg:white"),
        ]
    )

    config_path = questionary.path(
        "Enter Configuration file path:",
        only_directories=False,
        default="Config.xlsx",
        validate=is_valid_file_path,
    ).ask()

    task_path = questionary.path(
        "Enter Task file path:",
        only_directories=False,
        default="TaskList.xlsx",
        validate=is_valid_file_path,
    ).ask()

    errmsg_path = questionary.path(
        "Enter Error Message file path:",
        only_directories=False,
        default="ErrorMessages.xlsx",
        #        validate=is_valid_file_path,
    ).ask()

    input_path = questionary.path(
        "Enter Input folder path:",
        only_directories=True,
        default="Input",
        validate=is_valid_dir_path,
    ).ask()

    output_path = questionary.path(
        "Enter Output folder path:",
        only_directories=True,
        default="Output",
        validate=is_valid_dir_path,
    ).ask()

    # config_path = "Config.xlsx"
    # task_path = "TaskList.xlsx"
    # errmsg_path = "ErrorMessages.xlsx"
    # input_path = "Input"
    # output_path = "Output"

    print(BLUE + f"Configuration File path: {config_path}" + RESET)
    print(GREEN + f"Task File path: {task_path}" + RESET)
    print(PURPLE + f"Task File path: {errmsg_path}" + RESET)
    print(CYAN + f"Input folder path: {input_path}" + RESET)
    print(BLUE + f"Output folder path: {output_path}" + RESET)

    core = Core(config_path, task_path, errmsg_path, input_path, output_path)
    core.intialize()
    core.process_task()


if __name__ == "__main__":
    main()
