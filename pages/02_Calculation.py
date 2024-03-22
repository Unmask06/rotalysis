# main.py
import time

import streamlit as st

from rotalysis import Core, RotalysisInput
from utils import StreamlitObject

title = st.container().title("Rotalysis")

col1, col2 = st.container().columns(2)

with col1:
    input_folder = st.text_area(
        label="Input Folder Path", value="Input", key="input_folder"
    )
    output_folder = st.text_area(
        label="Output Folder Path", value="Output", key="output_folder"
    )


with col2:
    config_file = st.text_area(
        label="Configuration File Path", value="Config.xlsx", key="config_file"
    )
    tasklist_file = st.text_area(
        label="Task List", value="TaskList.xlsx", key="tasklist_file"
    )

input = RotalysisInput(
    INPUT_FOLDER=input_folder,
    OUTPUT_FOLDER=output_folder,
    CONFIG_FILE=config_file,
    TASKLIST_FILE=tasklist_file,
)

main_st_obj = StreamlitObject().component.progress(0)

run_button = st.button("Process Task", key="run_button")


def run():
    core = Core(input, main_st_obj)
    core.process_task()


if run_button:
    run()