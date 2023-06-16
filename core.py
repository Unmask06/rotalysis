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
from termcolor import colored


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
        total_tasks = len(self.dftask_list)

        progress_bar = tqdm(
            total=total_tasks,
            initial=0,
            bar_format="{desc}: {percentage:.0f}%\n{bar}",
            desc="Processing",
            unit="task",
        )

        for i in range(total_tasks):
            try:
                site, tag = self.dftask_list["Site"][i], self.dftask_list["Tag"][i]
                excel_path = UF.get_excel_path(site, tag)
                print("Processing: ", excel_path)
                dfprocess, dfoperation, dfcurve, dfunit = UF.load_equipment_data(excel_path)
                output_path = self.output_path
                PF.set_process_data(dfprocess)
                dfoperation = PF.remove_irrelevant_columns(dfoperation)
                PF.set_unit(dfunit)
                PF.convert_default_unit(dfoperation)

                try:
                    PF.check_mandatory_columns(dfoperation)

                except Exception as e:
                    print(colored("\n", e, "red"))

                dfoperation = PF.remove_abnormal_rows(dfoperation)

                try:
                    dfoperation = PF.get_computed_columns(dfoperation)

                except Exception as e:
                    print("Error occurred while computing columns: ", site, tag)
                    print(e)

                PF.create_energy_summary(dfoperation, output_path, site, tag)

            except Exception as e:
                # print(traceback.format_exc())
                print(colored("Error occurred while processing: ", "red"), site, tag)
                print("Error message saved to: ", self.errmsg_path)

            time.sleep(0.1)

            progress_bar.update(1)

        progress_bar.close()

        print("Task completed!")
