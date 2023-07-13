# pump.py in rotalysis folder
import os
import sys
from pathlib import Path

sys.path.append("..")

import numpy as np
import pandas as pd
import xlwings as xw

from rotalysis import PumpFunction as PF
from rotalysis import UtilityFunction as uf
from utils import Logger


class Pump:

    """
    Calculates the energy savings potential of a pump upon conversion to variable speed drive or trimming the impeller
    based on the operating data of the pump.

    Args:
        data_path (str): Path of the Excel file containing the operating data of the pump with the following sheets:
            1. process data
            2. operational data
            3. unit
            4. pump curve (optional)
        config_path (str, optional): Path of the Config.xlsx file. Defaults to "Config.xlsx".

    Returns:
        Dataframe: Energy savings summary of the pump for both VSD and impeller trimming case.

    Dependencies:
        - pump_function.py in rotalysis folder for pump static functions
        - utility_function.py in rotalysis folder for helper functions
        - valve_function.py in rotalysis folder
        - unit_converter.py in utils folder uses pint library for unit conversion
    """

    # ** Columns with units in Class Level
    mandatory_columns = {
        "suction_pressure": "barg",
        "discharge_pressure": "barg",
        "discharge_flowrate": "m3/h",
    }
    optional_columns = {
        "cv_opening": "%",
        "downstream_pressure": "barg",
        "motor_power": "kW",
        "recirculation_flow": "m3/h",
        "power_factor": "",
        "run_status": "",
        "speed": "rpm",
        "motor_amp": "A",
    }

    computed_columns = {
        "flowrate_percent": "%",
        "differential_pressure": "bar",
        "actual_cv": "gpm",
        "calculated_cv_drop": "bar",
        "measured_cv_drop": "bar",
        "cv_pressure_drop": "bar",
        "inherent_piping_loss": "bar",
        "required_differential_pressure": "bar",
        "required_speed_variation": "%",
        "base_hydraulic_power": "MW",
        "old_pump_efficiency": "%",
        "old_motor_efficiency": "%",
        "base_motor_power": "MW",
        "working_hours": "h",
        "working_percent": "%",
    }
    energy_columns = {
        "selected_measure": "",
        "selected_speed_variation": "%",
        "new_pump_efficiency": "%",
        "new_motor_efficiency": "%",
        "base_case_energy_consumption": "MWh",
        "proposed_case_energy_consumption": "MWh",
        "annual_energy_saving": "MWh",
    }
    emission_columns = {
        "base_case_emission": "tCO2e",
        "proposed_case_emission": "tCO2e",
        "ghg_reduction": "tCO2e",
        "ghg_reduction_percent": "%",
    }
    relevant_columns = list(mandatory_columns.keys()) + list(optional_columns.keys())

    def __init__(self, config_path="Config.xlsx", data_path=None):
        self.data_path = data_path
        self.config_path = config_path
        self.__set_data()
        self.logger = Logger(name=self.process_data["tag"]["value"])
        self.__set_config()
        self.__check_mandatory_columns()

    def __set_config(self):
        """
        INIT METHOD - Sets the config dictionary from the Config.xlsx file.
        """

        dfconfig = pd.read_excel(self.config_path, sheet_name="PumpConfig1", header=0)
        dfconfig = dfconfig.iloc[:, :3].dropna(subset=["parameter"])
        dfconfig.set_index("parameter", inplace=True)
        self.config = dfconfig.to_dict("index")

    def __set_data(self):
        """
        INIT METHOD - Sets the process data, operational data and unit dictionary from the Excel file.

        """
        if self.data_path is None:
            raise ValueError("data_path is not defined.")

        # Set Pump's process data
        dfprocess = pd.read_excel(self.data_path, sheet_name="process data", header=0)
        dfprocess = dfprocess.iloc[:, :3].dropna(subset=["process_data"])
        dfprocess.set_index("process_data", inplace=True)
        self.process_data = dfprocess.to_dict("index")

        # Set Pump operational data
        self.dfoperation = pd.read_excel(
            self.data_path,
            sheet_name="operational data",
            header=self.process_data["header_row"]["value"] - 1,
        )

        # Set Pump unit
        dfunit = pd.read_excel(self.data_path, sheet_name="unit", header=0)
        dfunit = dfunit.iloc[:, :2].dropna(subset=["unit"])
        self.unit = dict(zip(dfunit["parameter"], dfunit["unit"]))

    def __check_mandatory_columns(self):
        """
        INIT METHOD - Checks if the operational data excel sheet contains the mandatory columns.

        Raises:
            ValueError: If the operational data excel sheet is missing the mandatory columns.
        """
        missing_columns = [
            col for col in Pump.mandatory_columns if col not in self.dfoperation.columns
        ]
        if len(missing_columns) > 0:
            missing_columns_error = f"The operational data excel sheet is missing the following required columns: {', '.join(missing_columns)}."
            raise ValueError(missing_columns_error)

    def clean_non_numeric_data(self):
        """
        Cleans the non-numeric data from the operational data excel sheet

            ** Method called from utlity function module.
        """
        self.dfoperation = uf.Clean_dataframe(self.dfoperation)

    def remove_irrelevant_columns(self):
        irrelevant_columns = [
            col for col in self.dfoperation.columns if col not in Pump.relevant_columns
        ]
        self.dfoperation = self.dfoperation.drop(columns=irrelevant_columns)

    def convert_default_unit(self):
        flowrate_unit = self.unit["flowrate"]
        flowrate_conversion = {
            "m3/hr": 1,
            "default": 1,
            "BPD": 0.0066245,
            "gpm": 0.22712,
            "BPH": 0.15899,
        }
        self.dfoperation["discharge_flowrate"] = self.dfoperation[
            "discharge_flowrate"
        ] * flowrate_conversion.get(flowrate_unit, 1)

        pressure_unit = self.unit["pressure"]
        pressure_conversion = {"bar": 1, "psi": 0.0689476}

        self.dfoperation[
            ["suction_pressure", "discharge_pressure", "downstream_pressure"]
        ] = self.dfoperation[
            ["suction_pressure", "discharge_pressure", "downstream_pressure"]
        ] * pressure_conversion.get(
            pressure_unit, 1
        )

    def remove_non_operating_rows(self):
        """
        Remove rows non operating rows from dfoperationbasaed on the following criteria:
        1. discharge_flowrate > 0
        2. suction_pressure < discharge_pressure
        3. downstream_pressure < discharge_pressure

        """
        self.dfoperation.dropna(subset=Pump.mandatory_columns, inplace=True)

        calculation_method = self.process_data["calculation_method"]["value"]

        mask = pd.Series(True, index=self.dfoperation.index)  # Initialize mask as True for all rows
        mask &= self.dfoperation["discharge_flowrate"] > 0
        mask &= self.dfoperation["suction_pressure"] < self.dfoperation["discharge_pressure"]
        mask &= ~(
            (self.dfoperation["downstream_pressure"] > self.dfoperation["discharge_pressure"])
            & (self.dfoperation["downstream_pressure"].notna())
        )
        if calculation_method == "":
            raise ValueError("calculation_method is not defined in config file.")

        if (calculation_method == "downstream_pressure") and (
            "downstream_pressure" in self.dfoperation.columns
        ):
            downstream_pressure = pd.to_numeric(
                self.dfoperation["downstream_pressure"], errors="coerce"
            ).notna()
            mask &= (
                self.dfoperation["downstream_pressure"] < self.dfoperation["discharge_pressure"]
            ) & (downstream_pressure)

        elif calculation_method == "cv_opening" and "cv_opening" in self.dfoperation.columns:
            cv_opening = pd.to_numeric(self.dfoperation["cv_opening"], errors="coerce")
            mask &= (cv_opening.notna()) & (cv_opening > self.config["cv_opening_min"]["value"])
        else:
            raise ValueError("Invalid calculation method passed in the configuration file.")

        self.dfoperation = self.dfoperation.loc[mask].reset_index(drop=True)

    def __get_flowrate_percent(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the flowrate percentage for each row in the dataframe
        - Group the values based on the bin_percent specified in config file
        - The resulting binned values are stored in a new column 'flowrate_percent'
        """
        percent = self.config["bin_percent"]["value"]
        self.dfoperation["flowrate_percent"] = (
            self.dfoperation["discharge_flowrate"] / self.process_data["rated_flow"]["value"]
        )

        bins = np.arange(0.275, 1 + (5 * percent), percent)
        labels = np.arange(0.30, 1 + (5 * percent), percent)
        self.dfoperation["flowrate_percent"] = pd.cut(
            self.dfoperation["flowrate_percent"], bins=bins, labels=labels, right=True
        )

    def get_computed_columns(self):
        """
        - Computed columns for the pump operation data
        - Group the dfoperarion dataframe based on the flowrate percentage and create a new datframe "dfcalculation"

        ** Function are stored in the PumpFunction class.
        """
        density = self.process_data["density"]["value"]
        valve_size = self.process_data["valve_size"]["value"]
        valve_character = self.process_data["valve_character"]["value"]
        calculation_method = self.process_data["calculation_method"]["value"]

        # Add computed columns to dataframe
        self.dfoperation = self.dfoperation.reindex(
            columns=self.dfoperation.columns.tolist() + list(Pump.computed_columns.keys())
        )

        self.dfoperation["differential_pressure"] = PF.get_differential_pressure(
            self.dfoperation["discharge_pressure"], self.dfoperation["suction_pressure"]
        )

        if (valve_size != "") and (calculation_method == "cv_opening"):
            self.dfoperation["actual_cv"] = PF.get_actual_cv(
                valve_size, self.dfoperation["cv_opening"], valve_character
            )

            self.dfoperation["calculated_cv_drop"] = PF.get_calculated_cv_drop(
                self.dfoperation["discharge_flowrate"], self.dfoperation["actual_cv"], density
            )

        self.dfoperation["measured_cv_drop"] = PF.get_measured_cv_drop(
            self.dfoperation["discharge_pressure"], self.dfoperation["downstream_pressure"]
        )

        self.dfoperation["cv_pressure_drop"] = (
            self.dfoperation["measured_cv_drop"]
            if calculation_method == "downstream_pressure"
            else self.dfoperation["calculated_cv_drop"]
        )

        self.dfoperation["inherent_piping_loss"] = (
            self.dfoperation["cv_pressure_drop"] * self.config["pipe_loss"]["value"]
        )

        # calculate required differential pressure
        self.dfoperation["required_differential_pressure"] = (
            self.dfoperation["differential_pressure"]
            + self.dfoperation["inherent_piping_loss"]
            - self.dfoperation["cv_pressure_drop"]
        )

        # calculate required speed variation
        self.dfoperation["required_speed_variation"] = PF.get_speed_variation(
            self.dfoperation["differential_pressure"],
            self.dfoperation["required_differential_pressure"],
        )

        # calculate base case hydraulic power
        self.dfoperation["base_hydraulic_power"] = PF.get_base_hydraulic_power(
            self.dfoperation["discharge_flowrate"], self.dfoperation["differential_pressure"]
        )

        # calculate old pump efficiency
        BEP_flowrate = (
            self.process_data["rated_flow"]["value"]
            if self.process_data["BEP_flowrate"]["value"] == "" or (np.nan or None)
            else self.process_data["BEP_flowrate"]["value"]
        )
        BEP_efficiency = (
            self.config["pump_efficiency"]["value"]
            if self.process_data["BEP_efficiency"]["value"] == ""
            else self.process_data["BEP_efficiency"]["value"]
        )
        self.dfoperation["old_pump_efficiency"] = PF.get_pump_efficiency(
            BEP_flowrate, BEP_efficiency, self.dfoperation["discharge_flowrate"]
        )

        # calculate old_motor_efficiency
        self.dfoperation["old_motor_efficiency"] = self.process_data["motor_efficiency"]["value"]

        # calculate base case and proposed case motor power
        self.dfoperation["base_motor_power"] = (
            self.dfoperation["base_hydraulic_power"]
            / self.dfoperation["old_pump_efficiency"]
            / self.dfoperation["old_motor_efficiency"]
        )

        self.__get_flowrate_percent()

    def group_by_flowrate_percent(self):
        """
        - Group the dfoperation dataframe based on the flowrate percentage
        - Create a new datframe "dfcalculation"
        """
        df2 = self.dfoperation.groupby(by=["flowrate_percent"], as_index=False, dropna=False).mean(
            numeric_only=True
        )
        working_hours = self.dfoperation.groupby(
            by=["flowrate_percent"], as_index=False, dropna=False
        )["discharge_flowrate"].size()
        df2["working_hours"] = working_hours["size"]
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()

        df2.loc[
            df2["working_percent"] < self.config["min_working_percent"]["value"],
            ["working_hours", "working_percent"],
        ] = 0
        df2["working_percent"] = df2["working_hours"] / df2["working_hours"].sum()
        df2["working_hours"] = df2["working_percent"] * 8760
        df2 = df2.loc[df2["working_percent"] > 0].reset_index(drop=True)

        self.dfcalculation = df2

    def __select_speed_reduction(self):
        """
        Private method used in create_energy_calculation() method to select the speed reduction based on the options
        """

        self.dfcalculation.loc[
            self.dfcalculation["selected_measure"] == "Vsd", "selected_speed_variation"
        ] = self.dfcalculation["required_speed_variation"]

        self.dfcalculation.loc[
            (self.dfcalculation["selected_measure"] == "Impeller")
            & (self.dfcalculation["working_percent"] > 0),
            "selected_speed_variation",
        ] = (
            self.dfcalculation.loc[
                self.dfcalculation["working_percent"] > 0, "required_speed_variation"
            ]
            .dropna()
            .max()
        )

        self.dfcalculation.loc[
            (self.dfcalculation["working_percent"] <= 0), "selected_speed_variation"
        ] = 0

    def __get_energy_columns(self):
        """
        Private method used in create_energy_calculation() method to create energy related columns in dfcalculation dataframe.
        """

        # calculate base case annual energy consumption
        self.dfcalculation["base_case_energy_consumption"] = (
            self.dfcalculation["base_motor_power"] * self.dfcalculation["working_hours"]
        )

        # calculate proposed case efficiency
        self.dfcalculation["new_pump_efficiency"] = self.dfcalculation["old_pump_efficiency"]
        self.dfcalculation["new_motor_efficiency"] = self.dfcalculation["old_motor_efficiency"]

        # calculate proposed case annual energy consumption
        eff_factor = (
            self.dfcalculation["new_pump_efficiency"] * self.dfcalculation["new_motor_efficiency"]
        ) / (self.dfcalculation["old_pump_efficiency"] * self.dfcalculation["old_motor_efficiency"])

        self.dfcalculation["proposed_case_energy_consumption"] = (
            self.dfcalculation["base_case_energy_consumption"]
            * (self.dfcalculation["selected_speed_variation"] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        self.dfcalculation["annual_energy_saving"] = (
            self.dfcalculation["base_case_energy_consumption"]
            - self.dfcalculation["proposed_case_energy_consumption"]
        )

    def __get_emissions_columns(self):
        """
        Private method used in create_energy_calculation() method to create emissions related columns in dfcalculation dataframe.
        """
        emission_factor = self.config["emission_factor"]["value"]

        self.dfcalculation["base_case_emission"] = (
            self.dfcalculation["base_case_energy_consumption"] * emission_factor
        )

        self.dfcalculation["proposed_case_emission"] = (
            self.dfcalculation["proposed_case_energy_consumption"] * emission_factor
        )

        self.dfcalculation["ghg_reduction"] = (
            self.dfcalculation["base_case_emission"] - self.dfcalculation["proposed_case_emission"]
        )

        self.dfcalculation["ghg_reduction_percent"] = (
            self.dfcalculation["ghg_reduction"] / self.dfcalculation["base_case_emission"]
        )

    def create_energy_calculation(self):
        """
        - Create energy calculation dataframe for VSD and Impeller options.
        - Create summary dataframe for VSD and Impeller options.
        - Finally, renames the columns of all the dataframes from snake_case to Proper Case.
        """
        for option in ["Vsd", "Impeller"]:
            self.dfcalculation["selected_measure"] = option
            self.__select_speed_reduction()
            self.__get_energy_columns()
            self.__get_emissions_columns()

            if option == "Vsd":
                self.VSDCalculation = self.dfcalculation.copy()
                self.VSDSummary = self.__summarize(self.VSDCalculation)
                self.VSDSummary.columns = [option]
            elif option == "Impeller":
                self.ImpellerCalculation = self.dfcalculation.copy()
                self.ImpellerSummary = self.__summarize(self.ImpellerCalculation)
                self.ImpellerSummary.columns = [option]

        self.dfsummary = pd.concat([self.VSDSummary, self.ImpellerSummary], axis=1)
        self.__rename_columns()

    def __summarize(self, dfenergy):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Creates summary dataframe for VSDCalculation and ImpellerCalculation dataframe
        """
        columns = [
            "pump_tag",
            "rated_flowrate",
            "selected_speed_variation",
            "base_case_energy_consumption",
            "proposed_case_energy_consumption",
            "annual_energy_saving",
            "base_case_emission",
            "proposed_case_emission",
            "ghg_reduction",
            "ghg_reduction_percent",
        ]
        dfsummary = pd.DataFrame(columns=columns, data=np.nan, index=[0])
        dfsummary["pump_tag"] = self.process_data["tag"]["value"]
        dfsummary["rated_flowrate"] = self.process_data["rated_flow"]["value"]

        dfsummary["selected_speed_variation"] = (
            "{:.0%}".format(dfenergy["selected_speed_variation"].max())
            + " - "
            + "{:.0%}".format(dfenergy["selected_speed_variation"].min())
        )
        dfsummary["base_case_energy_consumption"] = dfenergy["base_case_energy_consumption"].sum()
        dfsummary["proposed_case_energy_consumption"] = dfenergy[
            "proposed_case_energy_consumption"
        ].sum()
        dfsummary["annual_energy_saving"] = dfenergy["annual_energy_saving"].sum()
        dfsummary["base_case_emission"] = dfenergy["base_case_emission"].sum()
        dfsummary["proposed_case_emission"] = dfenergy["proposed_case_emission"].sum()
        dfsummary["ghg_reduction"] = dfenergy["ghg_reduction"].sum()
        dfsummary["ghg_reduction_percent"] = (
            dfsummary["ghg_reduction"] / dfsummary["base_case_emission"]
        )
        dfsummary = dfsummary.transpose()

        return dfsummary

    def __rename_columns(self):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Renames the columns of all the dataframes from snake_case to Proper Case.
        """
        dfs = [j for j in vars(self).values() if isinstance(j, pd.DataFrame)]
        for df in dfs:
            df.rename(columns=lambda x: x.replace("_", " ").title(), inplace=True)
        self.dfsummary.index = self.dfsummary.index.str.replace("_", " ").str.title()

    def _add_multiheader(self):
        l1 = self.dfcalculation.columns.to_list()
        d1 = {
            **self.mandatory_columns,
            **self.optional_columns,
            **self.computed_columns,
            **self.energy_columns,
            **self.emission_columns,
        }
        multi_header = [(i, d1.get(i.replace(" ", "_").lower(), "")) for i in l1]

        self.VSDCalculation.columns = pd.MultiIndex.from_tuples(multi_header)
        self.ImpellerCalculation.columns = pd.MultiIndex.from_tuples(multi_header)

        self.dfsummary["Unit"] = [
            d1.get(i.replace(" ", "_").lower(), "") for i in self.dfsummary.index
        ]

    def _remove_multiheader(self):
        self.VSDCalculation.columns = self.VSDCalculation.columns.droplevel(1)
        self.ImpellerCalculation.columns = self.ImpellerCalculation.columns.droplevel(1)

    def _get_output_path(self, output_folder, site, tag):
        """
        PRIVATE METHOD used in  write_to_excel()

        Creates output path for excel file.
        """
        output_folder = Path(output_folder).resolve()
        output_folder_path = os.path.join(output_folder, site)
        os.makedirs(output_folder_path, exist_ok=True)
        output_path = os.path.join(output_folder_path, tag + ".xlsx")
        return output_path

    def write_to_excel(self, output_folder, site, tag):
        """
        Creates excel file based on the output folder, site and tag.
        Writes three dataframes to excel file.
        1. dfsummary
        2. VSDCalculation
        3. ImpellerCalculation

        """
        try:
            path = self._get_output_path(output_folder, site, tag)

            self._add_multiheader()

            if not os.path.isfile(path):
                wb = xw.Book()
            else:
                wb = xw.Book(path)
            with xw.App(visible=False) as app:
                ws = wb.sheets[0]
                ws.clear_contents()

                for cell, df, bool in zip(
                    ["A1", "A13", "A25"],
                    [self.dfsummary, self.VSDCalculation, self.ImpellerCalculation],
                    [True, False, False],
                ):
                    ws.range(cell).options(index=bool).value = df
                wb.save(path)
                wb.close()
                self._remove_multiheader()
        except Exception as e:
            raise Exception(e, "Error in writing to excel.")
