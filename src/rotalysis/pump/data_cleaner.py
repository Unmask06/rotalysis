""" This module leverages the pump_function.py module in the rotalysis folder
    to calculate the energy savings potential of a pump upon conversion to 
    variable speed drive or trimming the impeller based on the operating data
"""

import logging

import pandas as pd

from rotalysis import UtilityFunction as uf
from rotalysis.definitions import (
    ComputedVariables,
    EmissionVariables,
    InputSheetNames,
    PumpDesignDataVariables,
    PumpOperationVariables,
)

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """Custom Exception class for handling exceptions in the Pump module"""


class PumpDataCleaner:
    """
    Class to clean the operational data of the pump and
    set the relevant data for the pump optimization.
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
        PumpOperationVariables.RECIRCULATION_FLOW: "m3/h",
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

    operation_data: pd.DataFrame
    dfcalculation: pd.DataFrame

    def __init__(
        self,
        config: pd.DataFrame,
        process_data: pd.DataFrame,
        operation_data: pd.DataFrame,
        unit: pd.DataFrame,
    ):
        self.config = config
        self.process_data = process_data
        self.operation_data = operation_data
        self.unit = unit
        self.logger = logger

    def __set_config(self):
        """
        INIT METHOD - Sets the config dictionary from the Config.xlsx file.
        """

        dfconfig = self.config
        dfconfig = dfconfig.iloc[:, :3].dropna(subset=["parameter"])
        dfconfig.set_index("parameter", inplace=True)
        self.config = dfconfig.to_dict("index")

    def __set_data(self):
        """
        INIT METHOD- Sets the process data, operational data and unit dictionary

        """

        # Set Pump's process data
        dfprocess = self.process_data
        dfprocess = dfprocess.iloc[:, :3].dropna(subset=[InputSheetNames.DESIGN_DATA])
        dfprocess.set_index(InputSheetNames.DESIGN_DATA, inplace=True)
        self.process_data = dfprocess.to_dict("index")

        # Set Pump unit
        dfunit = self.unit.iloc[:, :2].dropna(subset=[InputSheetNames.UNIT])
        self.unit = dict(zip(dfunit["parameter"], dfunit[InputSheetNames.UNIT]))

    def __check_mandatory_columns(self):
        """
        INIT METHOD - Checks if the operational data excel sheet contains the mandatory columns.

        Raises:
            ValueError: If the operational data excel sheet is missing the mandatory columns.
        """
        missing_columns = [
            col
            for col in list(PumpDataCleaner.mandatory_columns.keys())
            if col not in self.operation_data.columns
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
        self.operation_data = uf.Clean_dataframe(self.operation_data)
        self.logger.info("Data cleaning completed")

    def remove_irrelevant_columns(self):
        irrelevant_columns = [
            col
            for col in self.operation_data.columns
            if col not in PumpDataCleaner.relevant_columns
        ]
        self.operation_data = self.operation_data.drop(columns=irrelevant_columns)
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

        self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE] = (
            self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE]
            * flowrate_conversion.get(flowrate_unit, 1)
        )

        self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"] = (
            self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"]
            * flowrate_conversion.get(flowrate_unit, 1)
        )

        pressure_unit = str(self.unit["pressure"])
        pressure_conversion = {"bar": 1, "psi": 0.0689476}

        self.operation_data[
            [
                PumpOperationVariables.SUCTION_PRESSURE,
                PumpOperationVariables.DISCHARGE_PRESSURE,
            ]
        ] = self.operation_data[
            [
                PumpOperationVariables.SUCTION_PRESSURE,
                PumpOperationVariables.DISCHARGE_PRESSURE,
            ]
        ] * pressure_conversion.get(
            pressure_unit, 1
        )

        if PumpOperationVariables.DOWNSTREAM_PRESSURE in self.operation_data.columns:
            self.operation_data[PumpOperationVariables.DOWNSTREAM_PRESSURE] = (
                self.operation_data[PumpOperationVariables.DOWNSTREAM_PRESSURE]
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
            self.operation_data.dropna(
                subset=list(PumpDataCleaner.mandatory_columns.keys()), inplace=True
            )

            calculation_method = self.process_data[
                PumpDesignDataVariables.CALCULATION_METHOD
            ]["value"]

            mask = pd.Series(
                True, index=self.operation_data.index
            )  # Initialize mask as True for all rows
            mask &= self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE] > 0
            mask &= (
                self.operation_data[PumpOperationVariables.SUCTION_PRESSURE]
                < self.operation_data[PumpOperationVariables.DISCHARGE_PRESSURE]
            )

            if uf.is_empty_value(calculation_method):
                raise CustomException(
                    "calculation_method is not defined in config file."
                )

            if (calculation_method == PumpOperationVariables.DOWNSTREAM_PRESSURE) and (
                PumpOperationVariables.DOWNSTREAM_PRESSURE
                in self.operation_data.columns
            ):
                downstream_pressure = pd.to_numeric(
                    self.operation_data[PumpOperationVariables.DOWNSTREAM_PRESSURE],
                    errors="coerce",
                ).notna()
                mask &= (
                    self.operation_data[PumpOperationVariables.DOWNSTREAM_PRESSURE]
                    < self.operation_data[PumpOperationVariables.DISCHARGE_PRESSURE]
                ) & (downstream_pressure)

            elif (
                calculation_method == PumpOperationVariables.CV_OPENING
                and PumpOperationVariables.CV_OPENING in self.operation_data.columns
            ):
                cv_opening = pd.to_numeric(
                    self.operation_data[PumpOperationVariables.CV_OPENING],
                    errors="coerce",
                )
                mask &= (cv_opening.notna()) & (
                    cv_opening > self.config["min_cv_opening"]["value"]
                )

            elif (
                f"{PumpOperationVariables.DOWNSTREAM_PRESSURE}|{PumpOperationVariables.CV_OPENING}"
                not in self.operation_data.columns
            ):
                error_msg = f"Can't find '{calculation_method}' column in operational data sheet.\n\
        Try changing the calculation_method or Add some data that column in operational data sheet."

                raise CustomException(error_msg)

            self.operation_data = self.operation_data.loc[mask].reset_index(drop=True)

        except (CustomException, KeyError) as e:
            raise CustomException(e) from e

    def set_computed_columns(self):

        self.operation_data = self.operation_data.reindex(
            columns=self.operation_data.columns.tolist()
            + list(PumpDataCleaner.computed_columns.keys())
        )

    def built_data_cleaner(self):
        self.__set_config()
        self.__set_data()
        self.__check_mandatory_columns()
        self.clean_non_numeric_data()
        self.remove_irrelevant_columns()
        self.convert_default_unit()
        self.remove_non_operating_rows()
        self.set_computed_columns()
