# core.py in rotalysis folder
import time
import traceback

from termcolor import colored

from rotalysis import Pump
from rotalysis import UtilityFunction as UF


class Core:
    def __init__(self, config_path, task_path, input_path, output_path, window=None):
        self.config_path = config_path
        self.task_path = task_path
        self.input_path = input_path
        self.output_path = output_path
        self.dftask_list = UF.load_task_list(task_path=self.task_path)
        self.window = window

    def process_task(self):
        total_tasks = len(self.dftask_list)

        for i in range(total_tasks):
            try:
                site, tag = self.dftask_list["Site"][i], self.dftask_list["Tag"][i]
                excel_path = UF.get_excel_path(self.input_path,site, tag)
                print("Processing: ", excel_path)

                p1 = Pump(config_path=self.config_path, data_path=excel_path)

                p1.clean_non_numeric_data()
                p1.remove_non_operating_rows()
                p1.convert_default_unit()
                p1.get_computed_columns()
                p1.group_by_flowrate_percent()
                p1.create_energy_calculation()
                p1.write_to_excel(self.output_path, site, tag)

            except Exception as e:
                print(traceback.format_exc())
                print(colored("Error occurred while processing: ", "red"), site, tag)
                print("Error message saved to: erro.log")

            time.sleep(0.1)

            progress = int((i + 1) / total_tasks * 100)
            if self.window:
                self.window.ProgressBar.setValue(progress)

        print("Task completed!")
