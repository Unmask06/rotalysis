# pump_function.py in rotalysis folder
import os
import sys

sys.path.append("..")

import numpy as np
import pandas as pd
import xlwings as xw
from termcolor import colored

from rotalysis import PumpFunction as PF
from rotalysis import UtilityFunction as uf
from rotalysis import ValveFunction


class Pump:
    def __init__(self, config_path="Config.xlsx", data_path=None, load_task_list=False):
        self.data_path = data_path
        self.config_path = config_path
        self.set_columns()
        self.set_config()
        self.set_data()
        self.check_mandatory_columns()

    def set_columns(self):
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
        self.mandatory_columns = mandatory_columns
        self.optional_columns = optional_columns
        self.relevant_columns = relevant_columns
        self.computed_columns = computed_columns
        self.energy_columns = energy_columns
        self.emission_columns = emission_columns


    def set_config(self):
        dfconfig = pd.read_excel(self.config_path, sheet_name="PumpConfig1", header=0)
        dfconfig = dfconfig.iloc[:, :3].dropna(subset=["parameter"])
        dfconfig.set_index("parameter", inplace=True)
        self.config = dfconfig.to_dict("index")

    def set_data(self):
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

    def check_mandatory_columns(self):
        missing_columns = [
            col for col in self.mandatory_columns if col not in self.dfoperation.columns
        ]
        if len(missing_columns) > 0:
            missing_columns_error = f"The operational data excel sheet is missing the following required columns: {', '.join(missing_columns)}."
            raise ValueError(missing_columns_error)

    def clean_non_numeric_data(self):
        self.dfoperation = uf.Clean_dataframe(self.dfoperation)

    def remove_irrelevant_columns(self):
        irrelevant_columns = [
            col for col in self.dfoperation.columns if col not in self.relevant_columns
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

        return self.dfoperation

    def remove_abnormal_rows(self):
        self.dfoperation.dropna(subset=self.mandatory_columns, inplace=True)

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

    def get_flowrate_percent(self):
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
        density = self.process_data["density"]["value"]
        valve_size = self.process_data["valve_size"]["value"]
        valve_character = self.process_data["valve_character"]["value"]
        calculation_method = self.process_data["calculation_method"]["value"]

        # Add computed columns to dataframe
        self.dfoperation = self.dfoperation.reindex(
            columns=self.dfoperation.columns.tolist() + self.computed_columns
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

        self.get_flowrate_percent()

    def group_by_flowrate_percent(self):
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

    def select_speed_reduction(self):
        self.dfcalculation.loc[
            self.dfcalculation["selected_option"] == "Vsd", "selected_speed_variation"
        ] = self.dfcalculation["required_speed_variation"]

        self.dfcalculation.loc[
            (self.dfcalculation["selected_option"] == "Impeller")
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

    def get_energy_columns(self):
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
        self.dfcalculation["annual_energy_savings"] = (
            self.dfcalculation["base_case_energy_consumption"]
            - self.dfcalculation["proposed_case_energy_consumption"]
        )

    def get_emissions_columns(self):
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
        for option in ["Vsd", "Impeller"]:
            self.dfcalculation["selected_option"] = option
            self.select_speed_reduction()
            self.get_energy_columns()
            self.get_emissions_columns()

            if option == "Vsd":
                self.VSDCalculation = self.dfcalculation
                self.VSDSummary = self.summarize(self.VSDCalculation)
                self.VSDSummary.columns = [option]
            elif option == "Impeller":
                self.ImpellerCalculation = self.dfcalculation
                self.ImpellerSummary = self.summarize(self.ImpellerCalculation)
                self.ImpellerSummary.columns = [option]

        self.dfsummary = pd.concat([self.VSDSummary, self.ImpellerSummary], axis=1)
        self._rename_columns()

    def summarize(self, dfenergy):
        columns = [
            "pump_tag",
            "rated_flowrate",
            "selected_speed_variation",
            "base_case_energy_consumption",
            "proposed_case_energy_consumption",
            "annual_energy_savings",
            "base_case_emission",
            "proposed_case_emission",
            "ghg_reduction",
            "ghg_reduction_percent",
        ]
        dfsummary = pd.DataFrame(columns=columns, data=np.nan, index=[0])
        dfsummary["pump_tag"] = self.process_data["tag_no"]["value"]
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
        dfsummary["annual_energy_savings"] = dfenergy["annual_energy_savings"].sum()
        dfsummary["base_case_emission"] = dfenergy["base_case_emission"].sum()
        dfsummary["proposed_case_emission"] = dfenergy["proposed_case_emission"].sum()
        dfsummary["ghg_reduction"] = dfenergy["ghg_reduction"].sum()
        dfsummary["ghg_reduction_percent"] = (
            dfsummary["ghg_reduction"] / dfsummary["base_case_emission"]
        )
        dfsummary = dfsummary.transpose()

        return dfsummary

    def _rename_columns(self):
        dfs = [j for j in vars(self).values() if isinstance(j, pd.DataFrame)]
        for df in dfs:
            df.rename(columns=lambda x: x.replace("_", " ").title(), inplace=True)
        self.dfsummary.index = self.dfsummary.index.str.replace("_", " ").str.title()

