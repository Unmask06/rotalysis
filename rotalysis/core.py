# core.py in rotalysis folder
import logging
import time
import traceback

from termcolor import colored

from rotalysis import Pump
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
        self.success = False

    def process_task(self):
        total_tasks = len(self.dftask_list)

        self.logger.info("\n" + 25 * "*"+ "Welcome to Rotalysis"+ "\n" + 25 * "*")
        self.logger.info(f"Total tasks to be processed: {total_tasks}")

        for i in range(total_tasks):
            try:
                site, tag = self.dftask_list["Site"][i], self.dftask_list["Tag"][i]
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
                p1.create_energy_calculation()
                p1.write_to_excel(self.output_path, site, tag)
                self.success = True

            except Exception as e:
                print(traceback.format_exc())
                self.logger.error(f"Error occurred while processing: {site}, {tag}")

            time.sleep(0.1)

            progress = int((i + 1) / total_tasks * 100)
            if self.window:
                self.window.ProgressBar.setValue(progress)
            self.logger.info("\n" + 25 * "-"+"\n")

        self.logger.info("Task completed!") if self.success else self.logger.error("Task failed!")
        self.logger.info("Please check the output folder for the result.") if self.success else None
        self.logger.info("\n" + 25 * "*"+ "Thanks for using Rotalysis"+ "\n" + 25 * "*")
