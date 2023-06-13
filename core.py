import pandas as pd
import numpy as np
import os
import time
from tqdm import tqdm
import xlwings as xw
from rotalysis import (
    UtilityFunction as UF,
    PumpFunction as PF,
    CompressorFunction as CF,
    ValveFunction as VF,
)
import traceback


class Core:
    def __init__(self, config_path, task_path, errmsg_path, input_path, output_path):
        self.config_path = config_path
        self.task_path = task_path
        self.errmsg_path = errmsg_path
        self.input_path = input_path
        self.output_path = output_path

    def intialize(self):
        PF.set_config(UF.load_config_pump(config_path=self.config_path))
        self.comp_cfg = UF.load_config_compressor(config_path=self.config_path)
        self.dftask_list = UF.load_task_list(task_path=self.task_path)

    def process_task(self):
        print(PF.config)
        print(self.comp_cfg)
        print(self.dftask_list.head())

        total_tasks = len(self.dftask_list)

        # Create a progress bar using tqdm
        progress_bar = tqdm(total=total_tasks, desc="Processing", unit="task")

        for i in range(total_tasks):
            try:
                site, tag = self.dftask_list["Site"][i], self.dftask_list["Tag"][i]
                excel_path = UF.get_excel_path(site, tag)
                print("Processing: ", excel_path)
                dfprocess, dfoperation, dfcurve, dfunit = UF.load_equipment_data(excel_path)
                PF.set_process_data(dfprocess)
                dfoperation = PF.remove_irrelevant_columns(dfoperation)
                PF.set_unit(dfunit)
                PF.convert_default_unit(dfoperation)

                try:
                    PF.check_mandatory_columns(dfoperation)
                except Exception as e:
                    print(e)

                dfoperation = PF.remove_abnormal_rows(dfoperation)


                dfoperation = PF.get_computed_columns(dfoperation)

                for option in ["VSD", "Impeller"]:
                    dfenergy = PF.create_energy_calculation(dfoperation, selected_option=option)
                    output_folder_path = os.path.join(os.getcwd(), self.output_path, site)
                    os.makedirs(output_folder_path, exist_ok=True)
                    output_file_path = os.path.join(output_folder_path, tag + ".xlsx")
                    UF.write_to_excel(output_file_path, option, dfenergy)
                print("Output file saved to: ", output_file_path)

            except Exception as e:
                print(traceback.format_exc())
                print("Error occurred while processing: ", site, tag)
                print("Error message saved to: ", self.errmsg_path)

            time.sleep(0.1)

            progress_bar.update(1)

        progress_bar.close()

        print("Task completed!")
        
config_path = "Config.xlsx"
task_path = "TaskList.xlsx"
errmsg_path = "ErrorMessages.xlsx"
input_path = "Input"
output_path = "Output"


trail = Core(config_path, task_path, errmsg_path, input_path, output_path)
trail.intialize()


i=0
site, tag = trail.dftask_list["Site"][i], trail.dftask_list["Tag"][i]
excel_path = UF.get_excel_path(site, tag)
dfprocess, dfoperation, dfcurve, dfunit = UF.load_equipment_data(excel_path)
PF.set_process_data(dfprocess)
dfoperation = PF.remove_irrelevant_columns(dfoperation)

PF.set_unit(dfunit)
PF.convert_default_unit(dfoperation)