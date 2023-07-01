import pandas as pd
import os
import xlwings as xw


class UtilityFunction:
    @staticmethod
    def load_task_list(task_path="TaskList.xlsx", sheet_name="task_list_1"):
        task_list = pd.read_excel(task_path, sheet_name=sheet_name, header=0).fillna("")
        task_list = task_list.loc[task_list["Perform"] == "Y"]
        task_list.reset_index(drop=True, inplace=True)
        return task_list

    @staticmethod
    def Clean_dataframe(df):
        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna(how="all")
        df = df.dropna(how="all", axis=1)
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def load_config_pump(config_path="config.xlsx", sheet_name="pump_config_1"):
        pump_config = pd.read_excel(config_path, sheet_name=sheet_name, index_col=0).fillna("")
        pump_config = pump_config.to_dict()
        pump_config = pump_config["value"]
        return pump_config

    @staticmethod
    def load_config_compressor(config_path="config.xlsx", sheet_name="compressor_config_1"):
        compressor_config = pd.read_excel(config_path, sheet_name=sheet_name, index_col=0).fillna(
            ""
        )
        compressor_config = compressor_config.to_dict()
        compressor_config = compressor_config["value"]
        return compressor_config

    @staticmethod
    def get_excel_path(site, tag):
        current_path = os.getcwd()

        subfolder_path = os.path.join(current_path, "Input", site)
        # check if subfolder exists

        try:
            if not os.path.exists(subfolder_path):
                raise NotADirectoryError("Site subfolder doesn't exist in Input directory.")
            files = os.listdir(subfolder_path)

            excel_files = [
                file
                for file in files
                if ((file.endswith(".xlsx") or file.endswith(".xls")) and tag in file)
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
    def write_to_excel(path: str, sheet_name: str, dataframe: pd.DataFrame) -> None:
        try:
            if not os.path.isfile(path):
                wb = xw.Book()
            else:
                wb = xw.Book(path)
            with xw.App(visible=False) as app:
                sheet_names = [sheet.name for sheet in wb.sheets]
                if sheet_name in sheet_names:
                    ws = wb.sheets[sheet_name]
                else:
                    ws = wb.sheets.add(sheet_name)
                ws.clear_contents()
                ws.range("A1").options(index=True).value = dataframe
                wb.save(path)
        except Exception as e:
            raise Exception(e, "Error in writing to excel.")
