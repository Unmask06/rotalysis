# core.py in rotalysis folder
import time
import traceback

from rotalysis import CustomException, Pump, RotalysisInput
from rotalysis import UtilityFunction as UF
from utils import streamlit_logger

from .definitions import EconomicsVariables, EmissionVariables


class Core:
    def __init__(self, rotalysis_input: RotalysisInput, window):
        self.input = rotalysis_input
        self.config_path = rotalysis_input.CONFIG_FILE
        self.task_path = rotalysis_input.TASKLIST_FILE
        self.input_path = rotalysis_input.INPUT_FOLDER
        self.output_path = rotalysis_input.OUTPUT_FOLDER
        self.dftask_list = UF.load_task_list(task_path=self.task_path)
        self.logger = streamlit_logger
        self.success_count = 0
        self.window = window

    def update_tasklist(self, pump: Pump, idx):
        task = self.dftask_list.loc[idx].copy()
        if self.success:
            task.update(
                {
                    "Perform": "N",
                    "Result": "Success",
                    "IT_energy": pump.df_summary["Impeller"][
                        EconomicsVariables.ANNUAL_ENERGY_SAVING
                    ],
                    "IT_ghg_cost": pump.df_economics["Impeller"][
                        EconomicsVariables.GHG_REDUCTION_COST
                    ],
                    "IT_ghg_reduction": pump.df_summary["Impeller"][
                        EmissionVariables.GHG_REDUCTION
                    ],
                    "IT_ghg_reduction_percent": pump.df_summary["Impeller"][
                        EmissionVariables.GHG_REDUCTION_PERCENT
                    ],
                    "VSD_energy": pump.df_summary["Vsd"][
                        EconomicsVariables.ANNUAL_ENERGY_SAVING
                    ],
                    "VSD_ghg_reduction": pump.df_summary["Vsd"][
                        EmissionVariables.GHG_REDUCTION
                    ],
                    "VSD_ghg_reduction_percent": pump.df_summary["Vsd"][
                        EmissionVariables.GHG_REDUCTION_PERCENT
                    ],
                    "VSD_ghg_cost": pump.df_economics["VSD"][
                        EconomicsVariables.GHG_REDUCTION_COST
                    ],
                }
            )
            self.dftask_list.loc[idx] = task

        else:
            self.dftask_list.loc[idx, ["Perform", "Result"]] = ["Y", "Failed"]

    def process_task(self):
        task_list = self.dftask_list.loc[self.dftask_list["Perform"] == "Y"]
        total_tasks = len(task_list)

        self.logger.info(f"\n{'*' * 30}Welcome to Rotalysis{'*' * 30}\n")
        self.logger.info(f"Total tasks to be processed: {total_tasks} \n")

        for i, (idx, row) in enumerate(task_list.iterrows()):
            self.success = False
            self.logger.info(f"Processing task {i+1} of {total_tasks}")
            try:
                site, tag = row["Site"], row["Tag"]
                self.logger.info(f"Searching Excel file for : {site}, {tag}")

                excel_path = UF.get_excel_path(self.input_path, site, tag)
                self.logger.info(f"Found excel path for processing:{excel_path}")

                pump = Pump(config_path=self.config_path, data_path=excel_path)

                pump.process_pump(output_folder=self.output_path, tag=tag, site=site)
                self.success = True
                self.success_count += 1

            except (CustomException, Exception) as e:
                self.logger.error(e)
                print(traceback.format_exc())

            time.sleep(0.1)

            progress = int((i + 1) / total_tasks)
            if self.window:
                self.window.progress(
                    progress, text=f"Processing {i+1} of {total_tasks} tasks"
                )
                (
                    self.logger.info("TASK COMPLETED!")
                    if self.success
                    else self.logger.critical("TASK FAILED!")
                )
                self.update_tasklist(pump, idx)  # type: ignore

                self.logger.info(f"\n{'-' * 50}\n")

        self.logger.info("Please check the output folder for the result.")
        self.logger.info(
            f"Total tasks processed: {self.success_count} out of {total_tasks}"
        )
        UF.write_to_excel(self.task_path, self.dftask_list)
        self.logger.info(f"\n{'*' * 30}Thanks for using Rotalysis{'*' * 30}\n")
