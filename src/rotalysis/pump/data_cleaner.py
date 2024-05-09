""" This module contains the PumpDataCleaner class which is responsible for cleaning 
the operational data of the pump and setting the relevant data for the PumpOptimizer. """

import logging

import numpy as np
import pandas as pd

from rotalysis import UtilityFunction as uf
from rotalysis.definitions import (
    ConfigurationVariables,
    EmissionVariables,
    InputSheetNames,
    PumpDesignDataVariables,
    PumpOperationVariables,
    PumpVariables,
)
from rotalysis.pump import PumpFunction as PF

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
        PumpVariables.FLOWRATE_PERCENT: "%",
        PumpVariables.DIFFERENTIAL_PRESSURE: "bar",
        PumpVariables.ACTUAL_CV: "gpm",
        PumpVariables.CALCULATED_CV_DROP: "bar",
        PumpVariables.MEASURED_CV_DROP: "bar",
        PumpVariables.CV_PRESSURE_DROP: "bar",
        PumpVariables.INHERENT_PIPING_LOSS: "bar",
        PumpVariables.REQUIRED_DIFFERENTIAL_PRESSURE: "bar",
        PumpVariables.REQUIRED_SPEED_VARIATION: "%",
        PumpVariables.BASE_HYDRAULIC_POWER: "MW",
        PumpVariables.OLD_PUMP_EFFICIENCY: "%",
        PumpVariables.OLD_MOTOR_EFFICIENCY: "%",
        PumpVariables.BASE_MOTOR_POWER: "MW",
        PumpVariables.WORKING_HOURS: "h",
        PumpVariables.WORKING_PERCENT: "%",
    }
    energy_columns = {
        PumpVariables.SELECTED_MEASURE: "",
        PumpVariables.SELECTED_SPEED_VARIATION: "%",
        PumpVariables.NEW_PUMP_EFFICIENCY: "%",
        PumpVariables.NEW_MOTOR_EFFICIENCY: "%",
        PumpVariables.BASE_CASE_ENERGY_CONSUMPTION: "MWh",
        PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION: "MWh",
        PumpVariables.ANNUAL_ENERGY_SAVING: "MWh",
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
        """
        Retuns the cleaned operational data for the pump optimization.

        Returns:
            self.operation_data: pd.DataFrame

        """
        self.__set_config()
        self.__set_data()
        self.__check_mandatory_columns()
        self.clean_non_numeric_data()
        self.remove_irrelevant_columns()
        self.convert_default_unit()
        self.remove_non_operating_rows()
        self.set_computed_columns()

    def __get_flowrate_percent(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Calculates the flowrate percentage for each row in the dataframe
        - Group the values based on the bin_percent specified in config file
        - The resulting binned values are stored in a new column 'flowrate_percent'
        """
        percent = self.config[ConfigurationVariables.BIN_PERCENT]["value"]
        self.operation_data[PumpVariables.FLOWRATE_PERCENT] = (
            self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE]
            / self.process_data[PumpDesignDataVariables.RATED_FLOWRATE]["value"]
        )

        bins = np.arange(0.275, 1 + (5 * percent), percent).tolist()
        labels = np.arange(0.30, 1 + (5 * percent), percent).tolist()
        self.operation_data[PumpVariables.FLOWRATE_PERCENT] = pd.cut(
            self.operation_data[PumpVariables.FLOWRATE_PERCENT],
            bins=bins,
            labels=labels,
            right=True,
        )

    def __check_recirculation(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        - Check if recirculation flow is greater than the discharge flow
        """
        if PumpOperationVariables.RECIRCULATION_FLOW in self.operation_data.columns:
            if (
                self.operation_data[PumpOperationVariables.RECIRCULATION_FLOW]
                > self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE]
            ).all():
                self.logger.warning("Recirculation flow is greater than discharge flow")

    def get_computed_columns(self):
        """
        Returns:
        self.operation_data: pd.DataFrame

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

        self.operation_data[PumpVariables.DIFFERENTIAL_PRESSURE] = (
            PF.get_differential_pressure(
                self.operation_data[PumpOperationVariables.DISCHARGE_PRESSURE],
                self.operation_data[PumpOperationVariables.SUCTION_PRESSURE],
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
                self.operation_data[PumpVariables.ACTUAL_CV] = PF.get_actual_cv(
                    valve_size,
                    self.operation_data[PumpOperationVariables.CV_OPENING],
                    valve_character,
                )

                self.operation_data[PumpVariables.CALCULATED_CV_DROP] = (
                    PF.get_calculated_cv_drop(
                        self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE],
                        self.operation_data[PumpVariables.ACTUAL_CV],
                        density,
                    )
                )
                self.operation_data[PumpVariables.CV_PRESSURE_DROP] = (
                    self.operation_data[PumpVariables.CALCULATED_CV_DROP]
                )
                self.operation_data[PumpVariables.INHERENT_PIPING_LOSS] = 0
            else:
                error_msg = "valve_size is not defined in config file."
                self.logger.error(error_msg)
                raise CustomException(error_msg)

        elif calculation_method == PumpOperationVariables.DOWNSTREAM_PRESSURE:
            self.operation_data[PumpVariables.MEASURED_CV_DROP] = (
                PF.get_measured_cv_drop(
                    self.operation_data[PumpOperationVariables.DISCHARGE_PRESSURE],
                    self.operation_data[PumpOperationVariables.DOWNSTREAM_PRESSURE],
                )
            )

            self.operation_data[PumpVariables.CV_PRESSURE_DROP] = self.operation_data[
                PumpVariables.MEASURED_CV_DROP
            ]
            self.operation_data[PumpVariables.INHERENT_PIPING_LOSS] = (
                self.operation_data[PumpVariables.CV_PRESSURE_DROP]
                * self.config[ConfigurationVariables.PIPING_LOSS]["value"]
            )

    def __get_required_differential_pressure(self):
        self.operation_data[PumpVariables.REQUIRED_DIFFERENTIAL_PRESSURE] = (
            self.operation_data[PumpVariables.DIFFERENTIAL_PRESSURE]
            + self.operation_data[PumpVariables.INHERENT_PIPING_LOSS]
            - self.operation_data[PumpVariables.CV_PRESSURE_DROP]
        )

    def __get_required_speed_varation(self):
        self.operation_data[PumpVariables.REQUIRED_SPEED_VARIATION] = (
            PF.get_speed_variation(
                self.operation_data[PumpVariables.DIFFERENTIAL_PRESSURE],
                self.operation_data[PumpVariables.REQUIRED_DIFFERENTIAL_PRESSURE],
            )
        )

    def __get_base_hydraulic_power(self):
        self.operation_data[PumpVariables.BASE_HYDRAULIC_POWER] = (
            PF.get_base_hydraulic_power(
                self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE],
                self.operation_data[PumpVariables.DIFFERENTIAL_PRESSURE],
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

        self.operation_data[PumpVariables.OLD_PUMP_EFFICIENCY] = PF.get_pump_efficiency(
            bep_flowrate,
            bep_efficiency,
            self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE],
        )

        # calculate old_motor_efficiency
        if uf.is_empty_value(
            self.process_data[PumpDesignDataVariables.MOTOR_EFFICIENCY]["value"]
        ):
            self.process_data[PumpDesignDataVariables.MOTOR_EFFICIENCY]["value"] = 0.9
            self.logger.warning(
                "motor_efficiency is empty. \n motor efficiency is considered 90% by default"
            )

        self.operation_data[PumpVariables.OLD_MOTOR_EFFICIENCY] = self.process_data[
            PumpDesignDataVariables.MOTOR_EFFICIENCY
        ]["value"]

    def __get_base_motor_power(self):
        """
        PRIVATE METHOD USED IN get_computed_columns()
        """
        self.operation_data[PumpVariables.BASE_MOTOR_POWER] = (
            self.operation_data[PumpVariables.BASE_HYDRAULIC_POWER]
            / self.operation_data[PumpVariables.OLD_PUMP_EFFICIENCY]
            / self.operation_data[PumpVariables.OLD_MOTOR_EFFICIENCY]
        )

    def __check_discharge_flow(self):
        """
        PRIVATE METHOD USED IN get_computed_columns() as quality check

        Raises:
            CustomException if the discharge flowrate is less than 30% of the rated flowrate
        """

        if (
            self.operation_data[PumpOperationVariables.DISCHARGE_FLOWRATE].max()
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
        df2 = self.operation_data.groupby(
            by=[PumpVariables.FLOWRATE_PERCENT],
            as_index=False,
            dropna=False,
            observed=False,
        ).mean(numeric_only=True)

        working_hours = self.operation_data.groupby(
            by=[PumpVariables.FLOWRATE_PERCENT],
            as_index=False,
            dropna=False,
            observed=False,
        )[PumpOperationVariables.DISCHARGE_FLOWRATE].size()

        df2[PumpVariables.WORKING_HOURS] = working_hours["size"]

        df2[PumpVariables.WORKING_PERCENT] = (
            df2[PumpVariables.WORKING_HOURS] / df2[PumpVariables.WORKING_HOURS].sum()
        )

        df2.loc[
            df2[PumpVariables.WORKING_PERCENT]
            < self.config[ConfigurationVariables.MIN_WORKING_PERCENT]["value"],
            [PumpVariables.WORKING_HOURS, PumpVariables.WORKING_PERCENT],
        ] = 0

        df2[PumpVariables.WORKING_PERCENT] = (
            df2[PumpVariables.WORKING_HOURS] / df2[PumpVariables.WORKING_HOURS].sum()
        )

        df2[PumpVariables.WORKING_HOURS] = df2[PumpVariables.WORKING_PERCENT] * 8760

        df2 = df2.loc[df2[PumpVariables.WORKING_PERCENT] > 0].reset_index(drop=True)
        df2[PumpVariables.WORKING_PERCENT] = (
            df2[PumpVariables.WORKING_HOURS] / df2[PumpVariables.WORKING_HOURS].sum()
        )

        df2[PumpVariables.WORKING_HOURS] = df2[PumpVariables.WORKING_PERCENT] * 8760

        self.dfcalculation = df2
