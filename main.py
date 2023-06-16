import questionary
from questionary import Style
from tqdm import tqdm
from art import text2art
import time
import os
from core import Core
from termcolor import colored


def animate_logo():
    company_name = "Tebodin"
    client_name = "ADNOC"
    program_name = "DECARB"
    clear_terminal()
    print(colored(text2art(company_name), "red"))
    time.sleep(1)
    clear_terminal()

    print(colored(text2art(client_name), "blue"))
    time.sleep(1)
    clear_terminal()

    print(colored(text2art(program_name), "green"))
    time.sleep(1)
    clear_terminal()


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

    print(colored(f"Configuration File path: {config_path}", "blue"))
    print(colored(f"Task File path: {task_path}", "green"))
    print(colored(f"Error Message File path: {errmsg_path}", "magenta"))
    print(colored(f"Input folder path: {input_path}", "cyan"))
    print(colored(f"Output folder path: {output_path}", "blue"))

    core = Core(config_path, task_path, errmsg_path, input_path, output_path)
    core.intialize()
    core.process_task()

    print(
        "Program finished successfully! \
        \nCheck the Error message and modify the input files accordingly and rerun the application."
    )
    close_program = questionary.confirm("Do you want to close the program?").ask()
    if close_program:
        print("Closing the program...")
    else:
        input("Press Enter to close the program...")


if __name__ == "__main__":
    main()
