import pandas as pd
import numpy as np
import os
from rotalysis import (
    UtilityFunction as UF,
    PumpFunction as PF,
    CompressorFunction as CF,
    ValveFunction as VF,
)


class Core:
    def __init__(self, config_path, task_path, errmsg_path, input_path, output_path):
        self.config_path = config_path
        self.task_path = task_path
        self.errmsg_path = errmsg_path
        self.input_path = input_path
        self.output_path = output_path

    def intialize(self):
        self.dfpump_cfg = UF.load_config_pump(config_path=self.config_path)
        self.dfcomp_cfg = UF.load_config_compressor(config_path=self.config_path)

        self.dftask_list = UF.load_task_list(task_path=self.task_path)
        # site, tag = task["Site"][0], task["Tag"][0]
        # excel_path = UF.get_excel_path(site, tag)

    def process_task(self):
        print(self.dfpump_cfg.head()), print(self.dfcomp_cfg.head()), print(self.dftask_list.head())


# pump_cfg = UF.load_config_pump()
# comp_cfg = UF.load_config_compressor()
# task = UF.load_task_list()
# site, tag = task["Site"][0], task["Tag"][0]

# excel_path = UF.get_excel_path(site, tag)
# print(excel_path)


# dfprocess, dfoperation, dfcurve, dfunit = UF.load_equipment_data(excel_path)

# dfoperation = pd.read_excel(file_path, sheet_name="operational data", header=ignore_rows)
# from VSDfunctions import UtilityFunctions as
# dfoperation = UtilityFunctions
