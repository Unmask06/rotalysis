""" This module leverages the pump_function.py module in the rotalysis folder
    to calculate the energy savings potential of a pump upon conversion to 
    variable speed drive or trimming the impeller based on the operating data
"""

import os
import traceback
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import numpy_financial as npf
import pandas as pd
import xlwings as xw
import xlwings.constants as xwc

from rotalysis import Economics as ec
from rotalysis import PumpFunction as PF
from rotalysis import UtilityFunction as uf
from rotalysis.definitions import (
    ComputedVariables,
    ConfigurationVariables,
    EconomicsVariables,
    EmissionVariables,
    InputSheetNames,
    PumpDesignDataVariables,
    PumpOperationVariables,
)
from utils import streamlit_logger


class CustomException(Exception):
    """Custom Exception class for handling exceptions in the Pump module"""


class Pump:
    """
    Calculates the energy savings potential of a pump upon conversion to
    variable speed drive or trimming the impeller based on the operating data of the pump.

    Args:
        data_path (str): Path of the Excel file containing the operating data of the pump
        with the following sheets:
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
        PumpOperationVariables.SUCTION_PRESSURE: "barg",
        PumpOperationVariables.DISCHARGE_PRESSURE: "barg",
        PumpOperationVariables.DISCHARGE_FLOWRATE: "m3/h",
    }
    optional_columns = {
        PumpOperationVariables.CV_OPENING: "%",
        PumpOperationVariables.DOWNSTREAM_PRESSURE: "barg",
        "motor_power": "kW",
        PumpOperationVariables.RECIRCULATION_FLOW: "m3/h",
        "power_factor": "",
        "run_status": "",
        "speed": "rpm",
        "motor_amp": "A",
    }

    computed_columns = {
        ComputedVariables.FLOWRATE_PERCENT: "%",
        ComputedVariables.DIFFERENTIAL_PRESSURE: "bar",
        ComputedVariables.ACTUAL_CV: "gpm",
        ComputedVariables.CALCULATED_CV_DROP: "bar",
        ComputedVariables.MEASURED_CV_DROP: "bar",
        ComputedVariables.CV_PRESSURE_DROP: "bar",
        ComputedVariables.INHERENT_PIPING_LOSS: "bar",
        ComputedVariables.REQUIRED_DIFFERENTIAL_PRESSURE: "bar",
        ComputedVariables.REQUIRED_SPEED_VARIATION: "%",
        ComputedVariables.BASE_HYDRAULIC_POWER: "MW",
        ComputedVariables.OLD_PUMP_EFFICIENCY: "%",
        ComputedVariables.OLD_MOTOR_EFFICIENCY: "%",
        ComputedVariables.BASE_MOTOR_POWER: "MW",
        ComputedVariables.WORKING_HOURS: "h",
        ComputedVariables.WORKING_PERCENT: "%",
    }
    energy_columns = {
        ComputedVariables.SELECTED_MEASURE: "",
        ComputedVariables.SELECTED_SPEED_VARIATION: "%",
        ComputedVariables.NEW_PUMP_EFFICIENCY: "%",
        ComputedVariables.NEW_MOTOR_EFFICIENCY: "%",
        ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION: "MWh",
        ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION: "MWh",
        ComputedVariables.ANNUAL_ENERGY_SAVING: "MWh",
    }
    emission_columns = {
        EmissionVariables.BASE_CASE_EMISSION: "tCO2e",
        EmissionVariables.PROPOSED_CASE_EMISSION: "tCO2e",
        EmissionVariables.GHG_REDUCTION: "tCO2e",
        EmissionVariables.GHG_REDUCTION_PERCENT: "%",
    }
    relevant_columns = list(mandatory_columns.keys()) + list(optional_columns.keys())

    dfoperation: pd.DataFrame
    dfcalculation: pd.DataFrame
    vsd_calculation: pd.DataFrame
    impeller_calculation: pd.DataFrame
    df_summary: pd.DataFrame
    vsd_summary: pd.DataFrame
    impeller_summary: pd.DataFrame
    vsd_economics: Dict[str, Any]
    impeller_economics: Dict[str, Any]
    vfd_economics: Dict[str, Any]
    df_economics: pd.DataFrame

    def __init__(self, config_path="Config.xlsx", data_path=None):
        self.data_path = data_path
        self.config_path = config_path
        self.__set_data()
        self.logger = streamlit_logger
        self.__set_config()
        self.get_emission_factor()
        self.__check_mandatory_columns()

    def __set_config(self):
        """
        INIT METHOD - Sets the config dictionary from the Config.xlsx file.
        """

        dfconfig = pd.read_excel(self.config_path, sheet_name="PumpConfig1", header=0)
        dfconfig = dfconfig.iloc[:, :3].dropna(subset=["parameter"])
        dfconfig.set_index("parameter", inplace=True)
        self.config = dfconfig.to_dict("index")

    def get_emission_factor(self):
        """
        Returns the emission factor from the config file.

        Returns:
            float: emission factor
        """
        dfemission_factor = pd.read_excel(
            self.config_path, sheet_name=EmissionVariables.EMISSION_FACTOR, header=0
        )
        dfemission_factor = dfemission_factor.iloc[:, :2].dropna(
            subset=[EmissionVariables.EMISSION_FACTOR]
        )
        dfemission_factor.set_index("site", inplace=True)
        self.dfemission_factor = dfemission_factor.to_dict("index")

    def __set_data(self):
        """
        INIT METHOD- Sets the process data, operational data and unit dictionary from the Excel file

        """
        if self.data_path is None:
            raise ValueError("data_path is not defined.")

        # Set Pump's process data
        dfprocess = pd.read_excel(
            self.data_path, sheet_name=InputSheetNames.DESIGN_DATA, header=0
        )
        dfprocess = dfprocess.iloc[:, :3].dropna(subset=[InputSheetNames.DESIGN_DATA])
        dfprocess.set_index(InputSheetNames.DESIGN_DATA, inplace=True)
        self.process_data = dfprocess.to_dict("index")

        # Set Pump operational data
        self.dfoperation = pd.read_excel(
            self.data_path,
            sheet_name=InputSheetNames.OPERATIONAL_DATA,
            header=self.process_data[PumpDesignDataVariables.HEADER_ROW]["value"] - 1,
        )

        # Set Pump unit
        dfunit = pd.read_excel(
            self.data_path, sheet_name=InputSheetNames.UNIT, header=0
        )
        dfunit = dfunit.iloc[:, :2].dropna(subset=[InputSheetNames.UNIT])
        self.unit = dict(zip(dfunit["parameter"], dfunit[InputSheetNames.UNIT]))

    def __check_mandatory_columns(self):
        """
        INIT METHOD - Checks if the operational data excel sheet contains the mandatory columns.

        Raises:
            ValueError: If the operational data excel sheet is missing the mandatory columns.
        """
        missing_columns = [
            col
            for col in list(Pump.mandatory_columns.keys())
            if col not in self.dfoperation.columns
        ]
        if len(missing_columns) > 0:
            missing_columns_error = f"Operational data excel sheet missing the required columns:\
                {', '.join(missing_columns)}."
            raise CustomException(missing_columns_error)

    def clean_non_numeric_data(self):
        """
        Cleans the non-numeric data from the operational data excel sheet

            ** Method called from utlity function module.
        """
        self.dfoperation = uf.Clean_dataframe(self.dfoperation)
        self.logger.info("Data cleaning completed")

    def remove_irrelevant_columns(self):
        irrelevant_columns = [
            col for col in self.dfoperation.columns if col not in Pump.relevant_columns
        ]
        self.dfoperation = self.dfoperation.drop(columns=irrelevant_columns)
        self.logger.info("Irrelevant columns removed")

    def convert_default_unit(self):
        flowrate_conversion = {
            "m3/hr": 1,
            "default": 1,
            "bpd": 0.0066245,
            "gpm": 0.22712,
            "bph": 0.15899,
            "mbph": 158.99,
        }

        flowrate_unit = self.unit["flowrate"].lower()
        if flowrate_unit not in flowrate_conversion:
            error_msg = f"Flowrate unit {flowrate_unit} is not supported.Supported units are\
                {', '.join(flowrate_conversion.keys())}"
            self.logger.error(error_msg)
            raise CustomException(error_msg)

        self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE] = self.dfoperation[
            PumpOperationVariables.DISCHARGE_FLOWRATE
        ] * flowrate_conversion.get(flowrate_unit, 1)

        self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"] = (
            self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"]
            * flowrate_conversion.get(flowrate_unit, 1)
        )

        pressure_unit = self.unit["pressure"]
        pressure_conversion = {"bar": 1, "psi": 0.0689476}

        self.dfoperation[
            [
                PumpOperationVariables.SUCTION_PRESSURE,
                PumpOperationVariables.DISCHARGE_PRESSURE,
            ]
        ] = self.dfoperation[
            [
                PumpOperationVariables.SUCTION_PRESSURE,
                PumpOperationVariables.DISCHARGE_PRESSURE,
            ]
        ] * pressure_conversion.get(
            pressure_unit, 1
        )

        if PumpOperationVariables.DOWNSTREAM_PRESSURE in self.dfoperation.columns:
            self.dfoperation[PumpOperationVariables.DOWNSTREAM_PRESSURE] = (
                self.dfoperation[PumpOperationVariables.DOWNSTREAM_PRESSURE]
                * pressure_conversion.get(pressure_unit, 1)
            )

        self.logger.info("unit conversion completed")

    def remove_non_operating_rows(self):
        """
        Remove rows non operating rows from dfoperationbasaed on the following criteria:
        1. discharge_flowrate > 0
        2. suction_pressure < discharge_pressure
        3. downstream_pressure < discharge_pressure

        """
        try:
            self.dfoperation.dropna(
                subset=list(Pump.mandatory_columns.keys()), inplace=True
            )

            calculation_method = self.process_data[
                PumpDesignDataVariables.CALCULATION_METHOD
            ]["value"]

            mask = pd.Series(
                True, index=self.dfoperation.index
            )  # Initialize mask as True for all rows
            mask &= self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE] > 0
            mask &= (
                self.dfoperation[PumpOperationVariables.SUCTION_PRESSURE]
                < self.dfoperation[PumpOperationVariables.DISCHARGE_PRESSURE]
            )

            if uf.is_empty_value(calculation_method):
                raise CustomException(
                    "calculation_method is not defined in config file."
                )

            if (calculation_method == PumpOperationVariables.DOWNSTREAM_PRESSURE) and (
                PumpOperationVariables.DOWNSTREAM_PRESSURE in self.dfoperation.columns
            ):
                downstream_pressure = pd.to_numeric(
                    self.dfoperation[PumpOperationVariables.DOWNSTREAM_PRESSURE],
                    errors="coerce",
                ).notna()
                mask &= (
                    self.dfoperation[PumpOperationVariables.DOWNSTREAM_PRESSURE]
                    < self.dfoperation[PumpOperationVariables.DISCHARGE_PRESSURE]
                ) & (downstream_pressure)

            elif (
                calculation_method == PumpOperationVariables.CV_OPENING
                and PumpOperationVariables.CV_OPENING in self.dfoperation.columns
            ):
                cv_opening = pd.to_numeric(
                    self.dfoperation[PumpOperationVariables.CV_OPENING],
                    errors="coerce",
                )
                mask &= (cv_opening.notna()) & (
                    cv_opening > self.config["min_cv_opening"]["value"]
                )

            elif (
                f"{PumpOperationVariables.DOWNSTREAM_PRESSURE}|{PumpOperationVariables.CV_OPENING}"
                not in self.dfoperation.columns
            ):
                error_msg = f"Can't find '{calculation_method}' column in operational data sheet.\n\
        Try changing the calculation_method or Add some data that column in operational data sheet."

                raise CustomException(error_msg)

            self.dfoperation = self.dfoperation.loc[mask].reset_index(drop=True)

        except (CustomException, KeyError) as e:
            raise CustomException(e) from e

    def __get_flowrate_percent(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the flowrate percentage for each row in the dataframe
        - Group the values based on the bin_percent specified in config file
        - The resulting binned values are stored in a new column 'flowrate_percent'
        """
        percent = self.config[ConfigurationVariables.BIN_PERCENT]["value"]
        self.dfoperation[ComputedVariables.FLOWRATE_PERCENT] = (
            self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE]
            / self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"]
        )

        bins = np.arange(0.275, 1 + (5 * percent), percent).tolist()
        labels = np.arange(0.30, 1 + (5 * percent), percent).tolist()
        self.dfoperation[ComputedVariables.FLOWRATE_PERCENT] = pd.cut(
            self.dfoperation[ComputedVariables.FLOWRATE_PERCENT],
            bins=bins,
            labels=labels,
            right=True,
        )

    def __check_recirculation(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Check if recirculation flow is greater than the discharge flow
        """
        if PumpOperationVariables.RECIRCULATION_FLOW in self.dfoperation.columns:
            if (
                self.dfoperation[PumpOperationVariables.RECIRCULATION_FLOW]
                > self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE]
            ).all():
                self.logger.warning("Recirculation flow is greater than discharge flow")

    def get_computed_columns(self):
        """
        - Computed columns for the pump operation data
        - Group the dfoperarion dataframe based on the flowrate percentage and
            create a new datframe "dfcalculation"

        ** Core functions are stored in the PumpFunction class
        """

        self.__add_computed_columns()
        self.__get_cv_drop()
        self.__get_required_differential_pressure()
        self.__get_required_speed_varation()
        self.__get_base_hydraulic_power()
        self.__get_efficiency()
        self.__get_base_motor_power()
        self.__check_recirculation()
        self.__check_discharge_flow()
        self.__get_flowrate_percent()

        self.logger.info("Computed columns added")

    def __add_computed_columns(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()

        """

        self.dfoperation = self.dfoperation.reindex(
            columns=self.dfoperation.columns.tolist()
            + list(Pump.computed_columns.keys())
        )

        self.dfoperation[ComputedVariables.DIFFERENTIAL_PRESSURE] = (
            PF.get_differential_pressure(
                self.dfoperation[PumpOperationVariables.DISCHARGE_PRESSURE],
                self.dfoperation[PumpOperationVariables.SUCTION_PRESSURE],
            )
        )

    def __get_cv_drop(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the cv_drop and inherant pipe loss based on the calculation_method
            1. downstream_pressure
            2. cv_opening
        """
        density = self.process_data[PumpDesignDataVariables.DENSITY]["value"]
        valve_size = self.process_data[PumpDesignDataVariables.DISCHARGE_VALVE_SIZE][
            "value"
        ]
        valve_character = self.process_data[
            PumpDesignDataVariables.DISCHARGE_VALVE_CHARACTER
        ]["value"]
        calculation_method = self.process_data[
            PumpDesignDataVariables.CALCULATION_METHOD
        ]["value"]

        if calculation_method == PumpOperationVariables.CV_OPENING:
            if not uf.is_empty_value(valve_size):
                self.dfoperation[ComputedVariables.ACTUAL_CV] = PF.get_actual_cv(
                    valve_size,
                    self.dfoperation[PumpOperationVariables.CV_OPENING],
                    valve_character,
                )

                self.dfoperation[ComputedVariables.CALCULATED_CV_DROP] = (
                    PF.get_calculated_cv_drop(
                        self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE],
                        self.dfoperation[ComputedVariables.ACTUAL_CV],
                        density,
                    )
                )
                self.dfoperation[ComputedVariables.CV_PRESSURE_DROP] = self.dfoperation[
                    ComputedVariables.CALCULATED_CV_DROP
                ]
                self.dfoperation[ComputedVariables.INHERENT_PIPING_LOSS] = 0
            else:
                error_msg = "valve_size is not defined in config file."
                self.logger.error(error_msg)
                raise CustomException(error_msg)

        elif calculation_method == PumpOperationVariables.DOWNSTREAM_PRESSURE:
            self.dfoperation[ComputedVariables.MEASURED_CV_DROP] = (
                PF.get_measured_cv_drop(
                    self.dfoperation[PumpOperationVariables.DISCHARGE_PRESSURE],
                    self.dfoperation[PumpOperationVariables.DOWNSTREAM_PRESSURE],
                )
            )

            self.dfoperation[ComputedVariables.CV_PRESSURE_DROP] = self.dfoperation[
                ComputedVariables.MEASURED_CV_DROP
            ]
            self.dfoperation[ComputedVariables.INHERENT_PIPING_LOSS] = (
                self.dfoperation[ComputedVariables.CV_PRESSURE_DROP]
                * self.config[ConfigurationVariables.PIPING_LOSS]["value"]
            )

    def __get_required_differential_pressure(self):
        self.dfoperation[ComputedVariables.REQUIRED_DIFFERENTIAL_PRESSURE] = (
            self.dfoperation[ComputedVariables.DIFFERENTIAL_PRESSURE]
            + self.dfoperation[ComputedVariables.INHERENT_PIPING_LOSS]
            - self.dfoperation[ComputedVariables.CV_PRESSURE_DROP]
        )

    def __get_required_speed_varation(self):
        self.dfoperation[ComputedVariables.REQUIRED_SPEED_VARIATION] = (
            PF.get_speed_variation(
                self.dfoperation[ComputedVariables.DIFFERENTIAL_PRESSURE],
                self.dfoperation[ComputedVariables.REQUIRED_DIFFERENTIAL_PRESSURE],
            )
        )

    def __get_base_hydraulic_power(self):
        self.dfoperation[ComputedVariables.BASE_HYDRAULIC_POWER] = (
            PF.get_base_hydraulic_power(
                self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE],
                self.dfoperation[ComputedVariables.DIFFERENTIAL_PRESSURE],
            )
        )

    def __get_bep_flowrate(self):
        """
        PRIVATE METHOD USED IN __get_efficiency()
        """
        bep_flowrate = self.process_data[PumpDesignDataVariables.BEP_FLOWRATE]["value"]
        if uf.is_empty_value(bep_flowrate):
            bep_flowrate = self.process_data[PumpDesignDataVariables.RATED_FLOWRATE][
                "value"
            ]
        elif isinstance(bep_flowrate, str):
            bep_flowrate = self.process_data[PumpDesignDataVariables.RATED_FLOWRATE][
                "value"
            ]
            self.logger.warning(
                "BEP_flowrate should be empty or numeric. Please don't string values next time.\n\
                    Rated flowrate is used as BEP_flowrate."
            )

        return bep_flowrate

    def __get_bep_efficiency(self):
        """
        PRIVATE METHOD USED IN __get_efficiency()
        """

        bep_efficiency = self.process_data[PumpDesignDataVariables.BEP_EFFICIENCY][
            "value"
        ]
        if uf.is_empty_value(bep_efficiency):
            bep_efficiency = self.config[ConfigurationVariables.PUMP_EFFICIENCY][
                "value"
            ]
        elif isinstance(bep_efficiency, str):
            bep_efficiency = self.config[ConfigurationVariables.PUMP_EFFICIENCY][
                "value"
            ]
            self.logger.warning(
                "BEP_efficiency should be empty or numeric. Please don't use string values.\
                    Default pump efficiency is used as BEP_efficiency."
            )

        return bep_efficiency

    def __get_efficiency(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        Calculates
            1. old_pump_efficiency
            2. old_motor_efficiency
        """
        bep_flowrate = self.__get_bep_flowrate()
        bep_efficiency = self.__get_bep_efficiency()

        self.dfoperation[ComputedVariables.OLD_PUMP_EFFICIENCY] = (
            PF.get_pump_efficiency(
                bep_flowrate,
                bep_efficiency,
                self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE],
            )
        )

        # calculate old_motor_efficiency
        if uf.is_empty_value(
            self.process_data[PumpDesignDataVariables.MOTOR_EFFICIENCY]["value"]
        ):
            self.process_data[PumpDesignDataVariables.MOTOR_EFFICIENCY]["value"] = 0.9
            self.logger.warning(
                "motor_efficiency is empty. \n motor efficiency is considered 90% by default"
            )

        self.dfoperation[ComputedVariables.OLD_MOTOR_EFFICIENCY] = self.process_data[
            PumpDesignDataVariables.MOTOR_EFFICIENCY
        ]["value"]

    def __get_base_motor_power(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        """
        self.dfoperation[ComputedVariables.BASE_MOTOR_POWER] = (
            self.dfoperation[ComputedVariables.BASE_HYDRAULIC_POWER]
            / self.dfoperation[ComputedVariables.OLD_PUMP_EFFICIENCY]
            / self.dfoperation[ComputedVariables.OLD_MOTOR_EFFICIENCY]
        )

    def __check_discharge_flow(self):
        """
        PRIVATE METHOD USED IN get_computed_columns() as quality check

        Raises:
            CustomException if the discharge flowrate is less than 30% of the rated flowrate
        """

        if (
            self.dfoperation[PumpOperationVariables.DISCHARGE_FLOWRATE].max()
            < 0.3 * self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"]
        ):
            error_msg = "The maximum flowrate is less than 30% of the rated flowrate. \n\
                Please check the flowrate unit."
            self.logger.warning(error_msg)

            raise CustomException(
                "Analysis stopped since VFD and Impeller trimming will not be effective."
            )

    def group_by_flowrate_percent(self):
        """
        - Group the dfoperation dataframe based on the flowrate percentage
        - Create a new datframe "dfcalculation"
        """
        df2 = self.dfoperation.groupby(
            by=[ComputedVariables.FLOWRATE_PERCENT],
            as_index=False,
            dropna=False,
            observed=False,
        ).mean(numeric_only=True)

        working_hours = self.dfoperation.groupby(
            by=[ComputedVariables.FLOWRATE_PERCENT],
            as_index=False,
            dropna=False,
            observed=False,
        )[PumpOperationVariables.DISCHARGE_FLOWRATE].size()

        df2[ComputedVariables.WORKING_HOURS] = working_hours["size"]

        df2[ComputedVariables.WORKING_PERCENT] = (
            df2[ComputedVariables.WORKING_HOURS]
            / df2[ComputedVariables.WORKING_HOURS].sum()
        )

        df2.loc[
            df2[ComputedVariables.WORKING_PERCENT]
            < self.config[ConfigurationVariables.MIN_WORKING_PERCENT]["value"],
            [ComputedVariables.WORKING_HOURS, ComputedVariables.WORKING_PERCENT],
        ] = 0

        df2[ComputedVariables.WORKING_PERCENT] = (
            df2[ComputedVariables.WORKING_HOURS]
            / df2[ComputedVariables.WORKING_HOURS].sum()
        )

        df2[ComputedVariables.WORKING_HOURS] = (
            df2[ComputedVariables.WORKING_PERCENT] * 8760
        )

        df2 = df2.loc[df2[ComputedVariables.WORKING_PERCENT] > 0].reset_index(drop=True)
        df2[ComputedVariables.WORKING_PERCENT] = (
            df2[ComputedVariables.WORKING_HOURS]
            / df2[ComputedVariables.WORKING_HOURS].sum()
        )

        df2[ComputedVariables.WORKING_HOURS] = (
            df2[ComputedVariables.WORKING_PERCENT] * 8760
        )

        self.dfcalculation = df2

    def __select_speed_reduction(self):
        """
        Private method used in create_energy_calculation() method
            to select the speed reduction based on the options
        """

        self.dfcalculation.loc[
            self.dfcalculation[ComputedVariables.SELECTED_MEASURE] == "Vsd",
            ComputedVariables.SELECTED_SPEED_VARIATION,
        ] = self.dfcalculation[ComputedVariables.REQUIRED_SPEED_VARIATION]

        self.dfcalculation.loc[
            (self.dfcalculation[ComputedVariables.SELECTED_MEASURE] == "Impeller")
            & (self.dfcalculation[ComputedVariables.WORKING_PERCENT] > 0),
            ComputedVariables.SELECTED_SPEED_VARIATION,
        ] = (
            self.dfcalculation.loc[
                self.dfcalculation[ComputedVariables.WORKING_PERCENT] > 0,
                ComputedVariables.REQUIRED_SPEED_VARIATION,
            ]
            .dropna()
            .max()
        )

        self.dfcalculation.loc[
            (self.dfcalculation[ComputedVariables.WORKING_PERCENT] <= 0),
            ComputedVariables.SELECTED_SPEED_VARIATION,
        ] = 0

    def __get_energy_columns(self):
        """
        Private method used in create_energy_calculation() method to create energy related columns
        in dfcalculation dataframe.
        """

        # calculate base case annual energy consumption
        self.dfcalculation[ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION] = (
            self.dfcalculation[ComputedVariables.BASE_MOTOR_POWER]
            * self.dfcalculation[ComputedVariables.WORKING_HOURS]
        )

        # calculate proposed case efficiency
        self.dfcalculation[ComputedVariables.NEW_PUMP_EFFICIENCY] = self.dfcalculation[
            ComputedVariables.OLD_PUMP_EFFICIENCY
        ]
        self.dfcalculation[ComputedVariables.NEW_MOTOR_EFFICIENCY] = self.dfcalculation[
            ComputedVariables.OLD_MOTOR_EFFICIENCY
        ]

        # calculate proposed case annual energy consumption
        eff_factor = (
            self.dfcalculation[ComputedVariables.NEW_PUMP_EFFICIENCY]
            * self.dfcalculation[ComputedVariables.NEW_MOTOR_EFFICIENCY]
        ) / (
            self.dfcalculation[ComputedVariables.OLD_PUMP_EFFICIENCY]
            * self.dfcalculation[ComputedVariables.OLD_MOTOR_EFFICIENCY]
        )

        self.dfcalculation[ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION] = (
            self.dfcalculation[ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION]
            * (self.dfcalculation[ComputedVariables.SELECTED_SPEED_VARIATION] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        self.dfcalculation[ComputedVariables.ANNUAL_ENERGY_SAVING] = (
            self.dfcalculation[ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION]
            - self.dfcalculation[ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION]
        )

    def __get_emissions_columns(self, site):
        """
        Private method used in create_energy_calculation method to create emissions related columns
        in dfcalculation dataframe.
        """
        emission_factor = self.dfemission_factor[site][
            EmissionVariables.EMISSION_FACTOR
        ]

        self.dfcalculation[EmissionVariables.BASE_CASE_EMISSION] = (
            self.dfcalculation[ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION]
            * emission_factor
        )

        self.dfcalculation[EmissionVariables.PROPOSED_CASE_EMISSION] = (
            self.dfcalculation[ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION]
            * emission_factor
        )

        self.dfcalculation[EmissionVariables.GHG_REDUCTION] = (
            self.dfcalculation[EmissionVariables.BASE_CASE_EMISSION]
            - self.dfcalculation[EmissionVariables.PROPOSED_CASE_EMISSION]
        )

        self.dfcalculation[EmissionVariables.GHG_REDUCTION_PERCENT] = (
            self.dfcalculation[EmissionVariables.GHG_REDUCTION]
            / self.dfcalculation[EmissionVariables.BASE_CASE_EMISSION]
        )

    def create_energy_calculation(self, site):
        """
        - Create energy calculation dataframe for VSD and Impeller options.
        - Create summary dataframe for VSD and Impeller options.
        - Finally, renames the columns of all the dataframes from snake_case to Proper Case.
        """
        for option in ["Vsd", "Impeller"]:
            self.dfcalculation[ComputedVariables.SELECTED_MEASURE] = option
            self.__select_speed_reduction()
            self.__get_energy_columns()
            self.__get_emissions_columns(site)

            if option == "Vsd":
                self.vsd_calculation = self.dfcalculation.copy()
                self.vsd_summary = self.__summarize(self.vsd_calculation, site)
                self.vsd_summary.columns = [option]
            elif option == "Impeller":
                self.impeller_calculation = self.dfcalculation.copy()
                self.impeller_summary = self.__summarize(
                    self.impeller_calculation, site
                )
                self.impeller_summary.columns = [option]

        self.df_summary = pd.concat([self.vsd_summary, self.impeller_summary], axis=1)

        if self.df_summary["Vsd"][ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION] == 0:
            error_msg = (
                "Base case energy consumption is zero. Please check the input data."
            )
            raise CustomException(error_msg)

        self.format_dataframes()
        self.logger.info("Energy calculation completed")

    def __summarize(self, dfenergy, site):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Creates summary dataframe for VSDCalculation and ImpellerCalculation dataframe
        """
        columns = [
            PumpDesignDataVariables.EQUIPMENT_TAG,
            PumpDesignDataVariables.RATED_FLOWRATE,
            ComputedVariables.SELECTED_SPEED_VARIATION,
            ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION,
            ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION,
            ComputedVariables.ANNUAL_ENERGY_SAVING,
            EmissionVariables.BASE_CASE_EMISSION,
            EmissionVariables.PROPOSED_CASE_EMISSION,
            EmissionVariables.GHG_REDUCTION,
            EmissionVariables.GHG_REDUCTION_PERCENT,
        ]
        df_summary = pd.DataFrame(columns=columns, data=np.nan, index=[0])
        df_summary[PumpDesignDataVariables.EQUIPMENT_TAG] = self.process_data[
            PumpDesignDataVariables.EQUIPMENT_TAG
        ]["value"]
        df_summary[PumpDesignDataVariables.RATED_FLOWRATE] = self.process_data[
            PumpDesignDataVariables.RATED_FLOWRATE
        ]["value"]

        df_summary[ComputedVariables.SELECTED_SPEED_VARIATION] = (
            f"{dfenergy[ComputedVariables.SELECTED_SPEED_VARIATION].max():.0%}"
            + " - "
            + f"{dfenergy[ComputedVariables.SELECTED_SPEED_VARIATION].min():.0%}"
        )
        df_summary[ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION] = dfenergy[
            ComputedVariables.BASE_CASE_ENERGY_CONSUMPTION
        ].sum()
        df_summary[ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION] = dfenergy[
            ComputedVariables.PROPOSED_CASE_ENERGY_CONSUMPTION
        ].sum()
        df_summary[ComputedVariables.ANNUAL_ENERGY_SAVING] = dfenergy[
            ComputedVariables.ANNUAL_ENERGY_SAVING
        ].sum()
        df_summary[EmissionVariables.BASE_CASE_EMISSION] = dfenergy[
            EmissionVariables.BASE_CASE_EMISSION
        ].sum()
        df_summary[EmissionVariables.PROPOSED_CASE_EMISSION] = dfenergy[
            EmissionVariables.PROPOSED_CASE_EMISSION
        ].sum()
        df_summary[EmissionVariables.EMISSION_FACTOR] = self.dfemission_factor[site][
            EmissionVariables.EMISSION_FACTOR
        ]
        df_summary[EmissionVariables.GHG_REDUCTION] = dfenergy[
            EmissionVariables.GHG_REDUCTION
        ].sum()
        df_summary[EmissionVariables.GHG_REDUCTION_PERCENT] = (
            df_summary[EmissionVariables.GHG_REDUCTION]
            / df_summary[EmissionVariables.BASE_CASE_EMISSION]
        )
        df_summary = df_summary.transpose()

        return df_summary

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

        self.vsd_calculation.columns = pd.MultiIndex.from_tuples(multi_header)
        self.impeller_calculation.columns = pd.MultiIndex.from_tuples(multi_header)

        self.df_summary["Unit"] = [
            d1.get(i.replace(" ", "_").lower(), "") for i in self.df_summary.index
        ]

    def _remove_multiheader(self):
        self.vsd_calculation.columns = self.vsd_calculation.columns.droplevel(1)
        self.impeller_calculation.columns = self.impeller_calculation.columns.droplevel(
            1
        )

    def get_economic_calculation(
        self, capex, opex, annual_energy_savings, annual_emission_reduction
    ) -> Dict[str, Union[str, float]]:
        discount_rate = self.config[ConfigurationVariables.DISCOUNT_RATE]["value"]
        project_life = self.config[ConfigurationVariables.PROJECT_LIFE]["value"]
        inflation_rate = self.config[ConfigurationVariables.INFLATION_RATE]["value"]
        electricity_price = self.config[ConfigurationVariables.ELECTRICITY_PRICE][
            "value"
        ]

        dfcashflow: pd.DataFrame = ec.create_cashflow_df(
            capex=capex, project_life=project_life
        )

        dfcashflow = dfcashflow.copy()

        dfcashflow[EconomicsVariables.FUEL_COST] = (
            annual_energy_savings * electricity_price
        )
        dfcashflow[EconomicsVariables.OPEX] = ec.inflation_adjusted_opex(
            opex, inflation_rate, years=dfcashflow.index
        )
        dfcashflow.loc[1:, EconomicsVariables.CASH_FLOW] = (
            dfcashflow[EconomicsVariables.FUEL_COST]
            - dfcashflow[EconomicsVariables.OPEX]
        )

        npv = npf.npv(
            rate=discount_rate, values=dfcashflow[EconomicsVariables.CASH_FLOW]
        )
        irr = npf.irr(dfcashflow[EconomicsVariables.CASH_FLOW])
        annualized_spending = ec.annualized_spending(npv, discount_rate, project_life)
        pay_back = ec.calculate_payback_period(dfcashflow[EconomicsVariables.CASH_FLOW])
        ghg_reduction_cost = ec.ghg_reduction_cost(
            annualized_spending, annual_emission_reduction
        )

        economic_calculation = {
            EconomicsVariables.CAPEX: round(capex, 0),
            EconomicsVariables.NPV: round(npv, 0),
            EconomicsVariables.IRR: f"{irr:.0%}",
            EconomicsVariables.PAYBACK_PERIOD: pay_back,
            EconomicsVariables.ANNUALIZED_SPENDING: round(annualized_spending, 0),
            EmissionVariables.ANNUAL_GHG_REDUCTION: round(annual_emission_reduction, 0),
            EconomicsVariables.GHG_REDUCTION_COST: round(ghg_reduction_cost, 0),
        }
        return economic_calculation

    def __get_economics(self):
        self.vsd_economics = self.get_economic_calculation(
            capex=self.config[ConfigurationVariables.VSD_CAPEX]["value"]
            / self.process_data[PumpDesignDataVariables.SPARING_FACTOR]["value"],
            opex=self.config[ConfigurationVariables.VSD_OPEX]["value"]
            * self.config[ConfigurationVariables.VSD_CAPEX]["value"],
            annual_energy_savings=self.df_summary["Vsd"][
                ComputedVariables.ANNUAL_ENERGY_SAVING
            ],
            annual_emission_reduction=self.df_summary["Vsd"][
                EmissionVariables.GHG_REDUCTION
            ],
        )

        self.vfd_economics = self.get_economic_calculation(
            capex=self.config[ConfigurationVariables.VFD_CAPEX]["value"]
            / self.process_data[PumpDesignDataVariables.SPARING_FACTOR]["value"],
            opex=self.config[ConfigurationVariables.VFD_OPEX]["value"]
            * self.config[ConfigurationVariables.VFD_CAPEX]["value"],
            annual_energy_savings=self.df_summary["Vsd"][
                ComputedVariables.ANNUAL_ENERGY_SAVING
            ],
            annual_emission_reduction=self.df_summary["Vsd"][
                EmissionVariables.GHG_REDUCTION
            ],
        )

        self.impeller_economics = self.get_economic_calculation(
            capex=self.config[ConfigurationVariables.IMPELLER_CAPEX]["value"]
            / self.process_data[PumpDesignDataVariables.SPARING_FACTOR]["value"],
            opex=self.config[ConfigurationVariables.IMPELLER_OPEX]["value"]
            * self.config[ConfigurationVariables.IMPELLER_CAPEX]["value"],
            annual_energy_savings=self.df_summary["Impeller"][
                ComputedVariables.ANNUAL_ENERGY_SAVING
            ],
            annual_emission_reduction=self.df_summary["Impeller"][
                EmissionVariables.GHG_REDUCTION
            ],
        )

    def get_economics_summary(self):
        try:
            self.__get_economics()

            dfs = []
            for option, col in zip(
                [self.vsd_economics, self.vfd_economics, self.impeller_economics],
                ["VSD", "VFD", "Impeller"],
            ):
                df = pd.DataFrame(
                    list(option.values()), index=list(option.keys()), columns=[col]
                )
                dfs.append(df)

            self.df_economics = pd.concat(dfs, axis=1)

        except Exception:
            self.logger.error("Error while creating economics summary.")
            print(traceback.format_exc())

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

    def format_dataframes(self):
        """
        Formats the dataframes for excel file.
        """
        percent_columns = [
            ComputedVariables.FLOWRATE_PERCENT,
            ComputedVariables.OLD_PUMP_EFFICIENCY,
            ComputedVariables.OLD_MOTOR_EFFICIENCY,
            ComputedVariables.NEW_MOTOR_EFFICIENCY,
            ComputedVariables.NEW_PUMP_EFFICIENCY,
            EmissionVariables.GHG_REDUCTION_PERCENT,
            ComputedVariables.REQUIRED_SPEED_VARIATION,
            ComputedVariables.SELECTED_SPEED_VARIATION,
            ComputedVariables.WORKING_PERCENT,
        ]
        for df in [self.vsd_calculation, self.impeller_calculation]:
            for col in percent_columns:
                df[col] = df[col].apply(
                    lambda x: uf.format_number(x, number_format="percent")
                )

            for col in df.columns:
                if df[col].dtype == "float64":
                    df[col] = df[col].apply(
                        lambda x: uf.format_number(x, number_format="whole")
                    )

    def write_to_excel(self, output_folder, site, tag):
        """
        Creates excel file based on the output folder, site and tag.
        Writes three dataframes to excel file.
        1. df_summary
        2. VSDCalculation
        3. ImpellerCalculation

        """
        try:
            path = self._get_output_path(output_folder, site, tag)

            self._add_multiheader()

            with xw.App(visible=False):
                if not os.path.isfile(path):
                    wb = xw.Book()
                else:
                    wb = xw.Book(path)
                ws = wb.sheets[0]
                ws.clear_contents()

                for cell, df, cond in zip(
                    ["A1", "A14", "A32", "G1"],
                    [
                        self.df_summary,
                        self.vsd_calculation,
                        self.impeller_calculation,
                        self.df_economics,
                    ],
                    [True, False, False, True],
                ):
                    ws.range(cell).options(index=cond).value = df
                    current_area = ws.range(cell).expand().address
                    # make boder
                    ws.range(current_area).api.Borders.LineStyle = 1

                ws.api.PageSetup.Orientation = xwc.PageOrientation.xlLandscape
                ws.api.PageSetup.PaperSize = xwc.PaperSize.xlPaperA3
                ws.api.PageSetup.PrintArea = "$A$1:$AG$50"
                ws.api.PageSetup.Zoom = 55
                ws.range("14:14").api.Font.Bold = True
                ws.range("14:14").api.Orientation = 90
                ws.range("32:32").api.Font.Bold = True
                ws.range("32:32").api.Orientation = 90
                ws.range("A:A").api.EntireColumn.AutoFit()

                pdf_path = path.replace(".xlsx", ".pdf")
                wb.api.ExportAsFixedFormat(0, pdf_path)
                wb.save(path)

                self._remove_multiheader()

                self.logger.info(f"Excel file created at {path}")
        except Exception as e:
            raise CustomException(e, "Error in writing to excel.") from e

    def process_pump(self, output_folder, site, tag):
        """
        Main method to run the pump analysis.
        """
        try:
            self.clean_non_numeric_data()
            self.remove_irrelevant_columns()
            self.convert_default_unit()
            self.remove_non_operating_rows()
            self.get_computed_columns()
            self.group_by_flowrate_percent()
            self.create_energy_calculation(site)
            self.get_economics_summary()
            self.write_to_excel(output_folder, site, tag)
        except CustomException as e:
            self.logger.error(e)
            raise CustomException(e) from e
        except Exception as e:
            self.logger.error(e)
            raise CustomException(e) from e
