import pandas as pd
import numpy as np
import xlwings as xw
import os
from termcolor import colored


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
                "Error in reading operational data. Check whether header row is correct. "
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
            raise Exception("Error in reading unit data.")

        return process_data, dfoperation, dfcurve, dfunit

    @staticmethod
    def write_to_excel(path: str, sheet_name: str, dataframe: pd.DataFrame) -> None:
        try:
            app = xw.App()
            if not os.path.isfile(path):
                wb = xw.Book()
            else:
                wb = xw.Book(path)
            ws = None
            sheet_names = [sheet.name for sheet in wb.sheets]
            if sheet_name in sheet_names:
                ws = wb.sheets[sheet_name]
            else:
                ws = wb.sheets.add(sheet_name)
            ws.clear_contents()
            ws.range("A1").options(index=False).value = dataframe
            wb.save(path)
            wb.close()
            app.quit()
        except Exception as e:
            raise Exception("Error in writing to excel.")


class ValveFunction:
    df_rated_cv = pd.DataFrame(
        {
            "valve_size": [0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12],
            "equal": [
                7.35,
                11.67,
                29.17,
                46.68,
                73.52,
                116.7,
                186.7,
                291.7,
                466.8,
                735.2,
                1000,
                1521,
            ],
            "linear": [
                8.05,
                12.84,
                20.54,
                51.35,
                80.52,
                128.4,
                205.4,
                320.9,
                513.5,
                805.2,
                1102,
                1680,
            ],
        }
    )

    @classmethod
    def get_linear_cv(cls, valve_size):
        return cls.df_rated_cv.loc[cls.df_rated_cv["valve_size"] == valve_size, "linear"].iloc[0]

    @classmethod
    def get_equal_cv(cls, valve_size):
        return cls.df_rated_cv.loc[cls.df_rated_cv["valve_size"] == valve_size, "equal"].iloc[0]

    @classmethod
    def get_rated_cv(cls, valve_size, valve_character):
        if valve_character == "Linear":
            rated_cv = cls.get_linear_cv(valve_size)
        elif valve_character == "Equal Percentage":
            rated_cv = cls.get_equal_cv(valve_size)
        return rated_cv

    @staticmethod
    def get_actual_cv(rated_cv, cv_opening, valve_character):
        if valve_character == "Linear":
            actual_cv = rated_cv * (cv_opening / 100)
        elif valve_character == "Equal Percentage":
            actual_cv = None
        return actual_cv

    @staticmethod
    def get_pressure_drop(discharge_flowrate, Cv, density):
        """
        Args:
            discharge_flowrate (float): discharge_flowrate in m3/hr
            Cv (float): CV in gpm
            density (float): Density in kg.m3.

        Returns:
            float: Control valve pressure drop in bar.

        """
        Cv = Cv / 1.156
        cv_pressure_drop = (discharge_flowrate / Cv) ** 2 * (density / 1000)
        return cv_pressure_drop


class PumpFunction:
    mandatory_columns = ["suction_pressure", "discharge_pressure", "discharge_flowrate"]
    optional_columns = [
        "cv_opening",
        "downstream_pressure",
        "motor_power",
        "recirculation_flow",
        "power_factor",
        "run_status",
        "speed",
        "motor_amp",
    ]

    relevant_columns = mandatory_columns + optional_columns
    computed_columns = [
        "flowrate_percent",
        "differential_pressure",
        "actual_cv",
        "calculated_cv_drop",
        "measured_cv_drop",
        "cv_pressure_drop",
        "inherent_piping_loss",
        "required_differential_pressure",
        "required_speed_variation",
        "base_hydraulic_power",
        "old_pump_efficiency",
        "old_motor_efficiency",
        "base_motor_power",
    ]
    energy_columns = [
        "selected_measure",
        "selected_speed_variation",
        "new_pump_efficiency",
        "new_motor_efficiency",
        "base_case_energy_consumption",
        "proposed_case_energy_consumption",
        "annual_energy_saving",
    ]
    emission_columns = [
        "base_case_emission",
        "proposed_case_emission",
        "annual_energy_savings",
        "ghg_reduction",
        "ghg_reduction_percent",
    ]
    config = None
    process_data = None

    @classmethod
    def set_config(cls, config):
        if not isinstance(config, dict):
            raise ValueError("config must be a dictionary.")
        cls.config = config

    @classmethod
    def set_process_data(cls, process_data):
        if not isinstance(process_data, dict):
            raise ValueError("process_data must be a dictionary.")
        cls.process_data = process_data
        density = PumpFunction.process_data["density"]
        valve_size = PumpFunction.process_data["valve_size"]
        valve_character = PumpFunction.process_data["valve_character"]
        calculation_method = PumpFunction.process_data["calculation_method"]

    @classmethod
    def set_unit(cls, unit):
        if not isinstance(unit, dict):
            raise ValueError("unit must be a dictionary.")
        cls.unit = unit

    @staticmethod
    def convert_default_unit(df):
        flowrate_unit = PumpFunction.unit["flowrate"]
        discharge_flowrate_conversion = {
            "m3/hr": 1,
            "default": 1,
            "BPD": 0.0066245,
            "gpm": 0.22712,
            "BPH": 0.15899,
        }
        df["discharge_flowrate"] = df["discharge_flowrate"] * discharge_flowrate_conversion.get(
            flowrate_unit, 1
        )

        pressure_unit = PumpFunction.unit["pressure"]
        pressure_conversion = {"bar": 1, "psi": 0.0689476}

        df[["suction_pressure", "discharge_pressure", "downstream_pressure"]] = df[
            ["suction_pressure", "discharge_pressure", "downstream_pressure"]
        ] * pressure_conversion.get(pressure_unit, 1)

        return df

    @staticmethod
    def check_mandatory_columns(df):
        missing_columns = [col for col in PumpFunction.mandatory_columns if col not in df.columns]
        if len(missing_columns) > 0:
            missing_columns_error = f"The operational data excel sheet is missing the following required columns: {', '.join(missing_columns)}."
            raise ValueError(
                f"The DataFrame is missing the following required columns: {', '.join(missing_columns)}."
            )

    @staticmethod
    def remove_irrelevant_columns(df):
        irrelevant_columns = [col for col in df.columns if col not in PumpFunction.relevant_columns]
        df = df.drop(columns=irrelevant_columns)
        return df

    @staticmethod
    def remove_abnormal_rows(df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame.")

        df.dropna(subset=PumpFunction.mandatory_columns, inplace=True)

        calculation_method = PumpFunction.process_data["calculation_method"]

        mask = pd.Series(True, index=df.index)  # Initialize mask as True for all rows
        mask &= df["discharge_flowrate"] > 0
        mask &= df["suction_pressure"] < df["discharge_pressure"]
        mask &= ~(
            (df["downstream_pressure"] > df["discharge_pressure"])
            & (df["downstream_pressure"].notna())
        )
        if calculation_method == "":
            raise ValueError("calculation_method is not defined in config file.")

        if (calculation_method == "downstream_pressure") and ("downstream_pressure" in df.columns):
            downstream_pressure = pd.to_numeric(df["downstream_pressure"], errors="coerce").notna()
            mask &= (df["downstream_pressure"] < df["discharge_pressure"]) & (downstream_pressure)
        elif calculation_method == "cv_opening" and "cv_opening" in df.columns:
            cv_opening = pd.to_numeric(df["cv_opening"], errors="coerce")
            mask &= (cv_opening.notna()) & (cv_opening > PumpFunction.config["cv_opening_min"])
        else:
            raise ValueError("Invalid calculation method passed in the configuration file.")

        df = df.loc[mask].reset_index(drop=True)
        return df

    @staticmethod
    def get_differential_pressure(discharge_pressure, suction_pressure):
        return discharge_pressure - suction_pressure

    @staticmethod
    def get_actual_cv(valve_size, cv_opening, valve_character):
        rated_cv = ValveFunction.get_rated_cv(valve_size, valve_character)
        actual_cv = ValveFunction.get_actual_cv(rated_cv, cv_opening, valve_character)
        return actual_cv

    @staticmethod
    def get_calculated_cv_drop(discharge_flowrate, actual_cv, density):
        calculated_cv_drop = ValveFunction.get_pressure_drop(discharge_flowrate, actual_cv, density)
        return calculated_cv_drop

    @staticmethod
    def get_measured_cv_drop(discharge_pressure, downstream_pressure):
        measured_cv_drop = discharge_pressure - downstream_pressure
        return measured_cv_drop

    @staticmethod
    def get_speed_variation(old_pressure, new_pressure):
        speed_variation = (new_pressure / old_pressure) ** (1 / 3)
        return speed_variation

    @staticmethod
    def get_base_hydraulic_power(discharge_flowrate, differential_pressure):
        """
        Args: discharge_flowrate in m3/hr, differential_pressure in bar
        Returns: hydraulic_power in MW
        """

        base_hydraulic_power = (
            (discharge_flowrate / 3600) * (differential_pressure * 10**5) / (10**6)
        )
        return base_hydraulic_power

    @staticmethod
    def get_proposed_hydraulic_power(base_hydralic_power, speed_variation):
        proposed_hydraulic_power = base_hydralic_power * (speed_variation**3)
        return proposed_hydraulic_power

    @staticmethod
    def get_flowrate_percent(df):
        percent = PumpFunction.config["bin_percent"]
        df["flowrate_percent"] = df["discharge_flowrate"] / PumpFunction.process_data["rated_flow"]

        bins = np.arange(0.275, 1 + (5 * percent), percent)
        labels = np.arange(0.30, 1 + (5 * percent), percent)
        df["flowrate_percent"] = pd.cut(
            df["flowrate_percent"], bins=bins, labels=labels, right=True
        )

        return df

    @staticmethod
    def get_pump_efficiency(BEP_flowrate, BEP_efficiency, actual_flowrate):
        correction_factor = 1 - ((1 - (actual_flowrate / BEP_flowrate)) ** 2)
        pump_efficiency = correction_factor * BEP_efficiency
        return pump_efficiency

    @staticmethod
    def get_computed_columns(df):
        density = PumpFunction.process_data["density"]
        valve_size = PumpFunction.process_data["valve_size"]
        valve_character = PumpFunction.process_data["valve_character"]

        # Add computed columns to dataframe
        df = df.reindex(columns=df.columns.tolist() + PumpFunction.computed_columns)

        df["differential_pressure"] = PumpFunction.get_differential_pressure(
            df["discharge_pressure"], df["suction_pressure"]
        )

        if (PumpFunction.process_data["valve_size"] != "") and (
            PumpFunction.process_data["calculation_method"] == "cv_opening"
        ):
            df["actual_cv"] = PumpFunction.get_actual_cv(
                valve_size, df["cv_opening"], valve_character
            )

            df["calculated_cv_drop"] = PumpFunction.get_calculated_cv_drop(
                df["discharge_flowrate"], df["actual_cv"], density
            )

        df["measured_cv_drop"] = PumpFunction.get_measured_cv_drop(
            df["discharge_pressure"], df["downstream_pressure"]
        )

        df["cv_pressure_drop"] = (
            df["measured_cv_drop"]
            if PumpFunction.process_data["calculation_method"] == "downstream_pressure"
            else df["calculated_cv_drop"]
        )

        df["inherent_piping_loss"] = df["cv_pressure_drop"] * PumpFunction.config["pipe_loss"]

        # calculate required differential pressure
        df["required_differential_pressure"] = (
            df["differential_pressure"] + df["inherent_piping_loss"] - df["cv_pressure_drop"]
        )

        # calculate required speed variation
        df["required_speed_variation"] = PumpFunction.get_speed_variation(
            df["differential_pressure"], df["required_differential_pressure"]
        )

        # calculate base case hydraulic power
        df["base_hydraulic_power"] = PumpFunction.get_base_hydraulic_power(
            df["discharge_flowrate"], df["differential_pressure"]
        )

        # calculate old pump efficiency
        BEP_flowrate = (
            PumpFunction.process_data["rated_flow"]
            if PumpFunction.process_data["BEP_flowrate"] == ""
            else PumpFunction.process_data["BEP_flowrate"]
        )
        BEP_efficiency = (
            PumpFunction.config["pump_efficiency"]
            if PumpFunction.process_data["BEP_efficiency"] == ""
            else PumpFunction.process_data["BEP_efficiency"]
        )
        df["old_pump_efficiency"] = PumpFunction.get_pump_efficiency(
            BEP_flowrate, BEP_efficiency, df["discharge_flowrate"]
        )

        # calculate old_motor_efficiency
        df["old_motor_efficiency"] = PumpFunction.process_data["motor_efficiency"]

        # calculate base case and proposed case motor power
        df["base_motor_power"] = (
            df["base_hydraulic_power"] / df["old_pump_efficiency"] / df["old_motor_efficiency"]
        )
        # df["proposed_motor_power"] = df["proposed_hydraulic_power"] / df["new_pump_efficiency"] / PumpFunction.process_data["motor_efficiency"]

        # calculate flowrate percent
        df = PumpFunction.get_flowrate_percent(df)
        return df

    @staticmethod
    def group_by_flowrate_percent(df):
        df2 = df.groupby(by=["flowrate_percent"], as_index=False, dropna=False).mean(
            numeric_only=True
        )
        working_hours = df.groupby(by=["flowrate_percent"], as_index=False, dropna=False)[
            "discharge_flowrate"
        ].size()
        df2["working_hours"] = working_hours["size"]
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()

        df2.loc[
            df2["working_percent"] < PumpFunction.config["min_working_percent"],
            ["working_hours", "working_percent"],
        ] = 0
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()
        df2["working_hours"] = df2["working_percent"] * 8760
        return df2

    @staticmethod
    def select_speed_reduction(dfEnergy):
        dfEnergy.loc[dfEnergy["selected_option"] == "VSD", "selected_speed_variation"] = dfEnergy[
            "required_speed_variation"
        ]
        dfEnergy.loc[
            (dfEnergy["selected_option"] == "Impeller") & (dfEnergy["working_percent"] > 0),
            "selected_speed_variation",
        ] = (
            dfEnergy.loc[dfEnergy["working_percent"] > 0, "required_speed_variation"].dropna().max()
        )
        dfEnergy.loc[(dfEnergy["working_percent"] <= 0), "selected_speed_variation"] = 0

        return dfEnergy

    @staticmethod
    def get_energy_columns(dfenergy):
        # calculate base case annual energy consumption
        dfenergy["base_case_energy_consumption"] = (
            dfenergy["base_motor_power"] * dfenergy["working_hours"]
        )

        # calculate proposed case efficiency
        dfenergy["new_pump_efficiency"] = dfenergy["old_pump_efficiency"]
        dfenergy["new_motor_efficiency"] = dfenergy["old_motor_efficiency"]

        # calculate proposed case annual energy consumption
        eff_factor = (dfenergy["new_pump_efficiency"] * dfenergy["new_motor_efficiency"]) / (
            dfenergy["old_pump_efficiency"] * dfenergy["old_motor_efficiency"]
        )
        dfenergy["proposed_case_energy_consumption"] = (
            dfenergy["base_case_energy_consumption"]
            * (dfenergy["selected_speed_variation"] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        dfenergy["annual_energy_savings"] = (
            dfenergy["base_case_energy_consumption"] - dfenergy["proposed_case_energy_consumption"]
        )

    @staticmethod
    def get_emissions_columns(dfEnergy):
        emission_factor = PumpFunction.config["emission_factor"]
        dfEnergy["base_case_emission"] = dfEnergy["base_case_energy_consumption"] * emission_factor
        dfEnergy["proposed_case_emission"] = (
            dfEnergy["proposed_case_energy_consumption"] * emission_factor
        )
        dfEnergy["ghg_reduction"] = (
            dfEnergy["base_case_emission"] - dfEnergy["proposed_case_emission"]
        )
        dfEnergy["ghg_reduction_percent"] = (
            dfEnergy["ghg_reduction"] / dfEnergy["base_case_emission"]
        )

    @staticmethod
    def create_energy_calculation(df, selected_option="VFD"):
        dfEnergy = PumpFunction.group_by_flowrate_percent(df)
        dfEnergy["selected_option"] = selected_option
        PumpFunction.select_speed_reduction(dfEnergy)
        PumpFunction.get_energy_columns(dfEnergy)
        PumpFunction.get_emissions_columns(dfEnergy)

        return dfEnergy

    @staticmethod
    def create_energy_summary(dfoperation, output_path, site, tag):
        for option in ["VSD", "Impeller"]:
            dfenergy = PumpFunction.create_energy_calculation(dfoperation, selected_option=option)
            output_folder_path = os.path.join(os.getcwd(), output_path, site)
            os.makedirs(output_folder_path, exist_ok=True)
            output_file_path = os.path.join(output_folder_path, tag + ".xlsx")
            UtilityFunction.write_to_excel(output_file_path, option, dfenergy)
        print("Output file saved to: ", output_file_path)


class CompressorFunction:
    @staticmethod
    def dummy(number, number2):
        return None
