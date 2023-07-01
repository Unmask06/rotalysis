# pump_function.py in rotalysis folder
import os

import numpy as np
import pandas as pd
import xlwings as xw
from termcolor import colored

from rotalysis import UtilityFunction, ValveFunction


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
    def create_energy_calculation(df, selected_option="VSD"):
        dfEnergy = PumpFunction.group_by_flowrate_percent(df)
        dfEnergy["selected_option"] = selected_option
        PumpFunction.select_speed_reduction(dfEnergy)
        PumpFunction.get_energy_columns(dfEnergy)
        PumpFunction.get_emissions_columns(dfEnergy)

        return dfEnergy

    @staticmethod
    def create_summary(dfenergy):
        dfenergy = dfenergy[dfenergy["working_percent"] > 0]
        columns = [
            "selected_speed_variation",
            "base_case_energy_consumption",
            "proposed_case_energy_consumption",
            "annual_energy_savings",
            "base_case_emission",
            "proposed_case_emission",
            "ghg_reduction",
            "ghg_reduction_percent",
        ]
        dfsummary = pd.DataFrame(columns=columns,data=np.nan,index=[0])
        dfsummary["pump_tag"] = PumpFunction.process_data["tag_no"]
        dfsummary["rated_flowrate"] = PumpFunction.process_data["rated_flow"]

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

        return dfsummary

    @staticmethod
    def save_energy_summary(dfoperation, output_path, site, tag):
        dfs = []
        for option in ["VSD", "Impeller"]:
            dfenergy = PumpFunction.create_energy_calculation(dfoperation, selected_option=option)
            dfsummary = PumpFunction.create_summary(dfenergy)
            dfsummary.index = [option]
            dfs.append(dfsummary)
            output_folder_path = os.path.join(os.getcwd(), output_path, site)
            os.makedirs(output_folder_path, exist_ok=True)
            output_file_path = os.path.join(output_folder_path, tag + ".xlsx")
            UtilityFunction.write_to_excel(output_file_path, option, dfenergy)
        print("Output file saved to: ", output_file_path)

        dfsummary = pd.concat(dfs)
        dfsummary = dfsummary.transpose()
        UtilityFunction.write_to_excel(output_file_path, "Summary", dfsummary)
