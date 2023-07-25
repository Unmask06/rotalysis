import os
from pathlib import Path

import pandas as pd
import xlwings as xw

from utils import logger


class UtilityFunction:
    excel_number_fomrat = {
        "acc_dec": "_-* #,##0.0_-",
        "acc_integer": "_-* #,##0_-",
        "percent_int": "0%",
        "percent_dec": "0.0%",
    }

    @staticmethod
    def load_task_list(task_path="TaskList.xlsx", sheet_name=0):
        task_list = pd.read_excel(task_path, sheet_name=sheet_name, header=0).fillna("")
        # task_list = task_list.loc[task_list["Perform"] == "Y"]
        # task_list.reset_index(drop=True, inplace=True)
        return task_list

    @staticmethod
    def Clean_dataframe(df):
        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna(how="all")
        df = df.dropna(how="all", axis=1)
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def get_excel_path(input_folder, site, tag):
        current_path = Path(input_folder).resolve()

        subfolder_path = os.path.join(current_path, site)

        try:
            if not os.path.exists(subfolder_path):
                raise NotADirectoryError("Site subfolder doesn't exist in Input directory.")
            files = os.listdir(subfolder_path)

            excel_files = [
                file
                for file in files
                if (
                    (file.endswith(".xlsx") or file.endswith(".xls"))
                    and tag in file.replace(" ", "")
                )
            ]

            if len(excel_files) > 0:
                excel_path = os.path.join(subfolder_path, excel_files[0])
            else:
                raise FileNotFoundError(
                    f'Excel file not found with "{tag}" tag in the "{site}" sub-folder of Input directory.'
                )

            return excel_path
        except Exception as e:
            print(e)

    @staticmethod
    def load_equipment_data(excel_path):
        try:
            process_data = pd.read_excel(excel_path, sheet_name="process data", index_col=0).fillna(
                ""
            )
            process_data = process_data.to_dict()
            process_data = process_data["value"]
            header_row = process_data["header_row"]
            equipment_type = process_data["equipment_type"]
            ignore_rows = header_row - 1
        except Exception as e:
            raise Exception("Error in reading process data.")

        try:
            dfoperation = pd.read_excel(
                excel_path, sheet_name="operational data", header=ignore_rows
            )
            dfoperation = UtilityFunction.Clean_dataframe(dfoperation)

        except Exception as e:
            raise Exception(
                e, "Error in reading operational data. Check whether header row is correct. "
            )

        try:
            if equipment_type == "Pump":
                dfcurve = pd.read_excel(excel_path, sheet_name="pump curve")
            elif equipment_type == "Compressor":
                dfcurve = pd.read_excel(excel_path, sheet_name="compressor curve")

        except Exception as e:
            raise Exception("Error in reading curve data.")
        try:
            dfunit = pd.read_excel(excel_path, sheet_name="unit", usecols="A:B")
            dfunit.dropna(inplace=True)
            dfunit = dict(zip(dfunit["parameter"], dfunit["unit"]))
        except Exception as e:
            raise Exception(e, "Error in reading unit data.")

        return process_data, dfoperation, dfcurve, dfunit

    @staticmethod
    def write_to_excel(path: str, dataframe, sheet_name=0, cell: str = "A1") -> None:
        try:
            with xw.App(visible=False) as app:
                if not os.path.isfile(path):
                    wb = xw.Book()
                else:
                    wb = xw.Book(path)
                    ws = wb.sheets[sheet_name]
                    ws.clear_contents()
                    ws.range(cell).options(index=False).value = dataframe
                    wb.save(path)
        except Exception as e:
            raise Exception(e, "Error in writing to excel.")
