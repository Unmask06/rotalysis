# core.py in rotalysis folder
import logging
import time
import traceback

from rotalysis import CustomException, Pump
from rotalysis import UtilityFunction as UF
from utils import logger


class Core:
    def __init__(self, config_path, task_path, input_path, output_path, window=None):
        self.config_path = config_path
        self.task_path = task_path
        self.input_path = input_path
        self.output_path = output_path
        self.dftask_list = UF.load_task_list(task_path=self.task_path)
        self.window = window
        self.logger = logger
        self.success_count = 0

    def update_tasklist(self, pump, idx):
        if self.success:
            self.dftask_list.loc[idx, ["Perform", "Result"]] = ("N", "Success")
            self.dftask_list.loc[idx, "IT_energy"] = pump.dfSummary["Impeller"]["Annual Energy Saving"]
            self.dftask_list.loc[idx, "IT_ghg_cost"] = pump.dfEconomics["Impeller"]["GHG Reduction Cost"]
            self.dftask_list.loc[idx, "IT_ghg_reduction"] = pump.dfSummary["Impeller"]["Ghg Reduction"]
            self.dftask_list.loc[idx, "IT_ghg_reduction_percent"] = pump.dfSummary["Impeller"]["Ghg Reduction Percent"]
            self.dftask_list.loc[idx, "IT_ghg_cost"] = pump.dfEconomics["Impeller"]["GHG Reduction Cost"]
            self.dftask_list.loc[idx, "VSD_energy"] = pump.dfSummary["Vsd"]["Annual Energy Saving"]
            self.dftask_list.loc[idx, "VSD_ghg_reduction"] = pump.dfSummary["Vsd"]["Ghg Reduction"]
            self.dftask_list.loc[idx, "VSD_ghg_reduction_percent"] = pump.dfSummary["Vsd"]["Ghg Reduction Percent"]
            self.dftask_list.loc[idx, "VSD_ghg_cost"] = pump.dfEconomics["VSD"]["GHG Reduction Cost"]

        else:
            self.dftask_list.loc[idx, ["Perform", "Result"]] = ("Y", "Failed")

    def process_task(self):
        task_list = self.dftask_list.loc[self.dftask_list["Perform"] == "Y"]
        total_tasks = len(task_list)

        self.logger.info("\n" + 30 * "*" + "Welcome to Rotalysis" + 30 * "*" + "\n")
        self.logger.info(f"Total tasks to be processed: {total_tasks} \n")

        for i, (idx, row) in enumerate(task_list.iterrows()):
            self.success = False
            self.logger.info(f"Processing task {i+1} of {total_tasks}")
            try:
                site, tag = row["Site"], row["Tag"]
                self.logger.info(f"Searching Excel file for : {site}, {tag}")

                excel_path = UF.get_excel_path(self.input_path, site, tag)
                self.logger.info(f"Found excel path for processing:{excel_path}")

                p1 = Pump(config_path=self.config_path, data_path=excel_path)

                p1.clean_non_numeric_data()
                p1.remove_irrelevant_columns()
                p1.remove_non_operating_rows()
                p1.convert_default_unit()
                p1.get_computed_columns()
                p1.group_by_flowrate_percent()
                p1.create_energy_calculation(site)
                p1.get_economics_summary()
                p1.write_to_excel(self.output_path, site, tag)
                self.success = True
                self.success_count += 1

            except (CustomException, Exception) as e:
                self.logger.error(e)
                print(traceback.format_exc())

            time.sleep(0.1)

            progress = int((i + 1) / total_tasks * 100)
            if self.window:
                self.window.ProgressBar.setValue(progress)
                self.logger.info("TASK COMPLETED!") if self.success else self.logger.critical("TASK FAILED!")
                self.update_tasklist(p1, idx)

                self.logger.info("\n" + 50 * "-" + "\n")

        self.logger.info("Please check the output folder for the result.")
        self.logger.info(f"Total tasks processed: {self.success_count} out of {total_tasks}")
        UF.write_to_excel(self.task_path, self.dftask_list)
        self.logger.info("\n" + 30 * "*" + "Thanks for using Rotalysis" + 30 * "*" + "\n")
