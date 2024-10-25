""" This module leverages the pump_function.py module in the rotalysis folder
    to calculate the energy savings potential of a pump upon conversion to 
    variable speed drive or trimming the impeller based on the operating data
"""

import logging
import os
import traceback
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import numpy_financial as npf
import pandas as pd

from rotalysis import Economics as ec
from rotalysis import UtilityFunction as uf
from rotalysis.definitions import (
    ConfigurationVariables,
    EconomicsVariables,
    EmissionVariables,
    PumpDesignDataVariables,
    PumpOperationVariables,
    PumpVariables,
)

from .data_cleaner import PumpDataCleaner
from .pump_function import PumpFunction as PF

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """Custom Exception class for handling exceptions in the Pump module"""


class PumpOptimizer:
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

    def __init__(
        self,
        emission_factor: pd.DataFrame,
        pump_data: PumpDataCleaner,
    ):
        self.pump_data = pump_data
        pump_data.built_data_cleaner()
        self.config = pump_data.config
        self.emission_factor = emission_factor
        self.process_data = pump_data.process_data
        self.operation_data = pump_data.operation_data
        self.unit = pump_data.unit
        self.logger = logger
        # self.get_emission_factor()

    # def get_emission_factor(self):
    #     """
    #     Returns the emission factor from the config file.

    #     Returns:
    #         float: emission factor
    #     """
    #     dfemission_factor = self.emission_factor
    #     dfemission_factor = dfemission_factor.iloc[:, :2].dropna(
    #         subset=[EmissionVariables.EMISSION_FACTOR]
    #     )
    #     dfemission_factor.set_index("site", inplace=True)
    #     self.dfemission_factor = dfemission_factor.to_dict("index")

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

    def __select_speed_reduction(self):
        """
        Private method used in create_energy_calculation() method
            to select the speed reduction based on the options
        """

        self.dfcalculation.loc[
            self.dfcalculation[PumpVariables.SELECTED_MEASURE] == "Vsd",
            PumpVariables.SELECTED_SPEED_VARIATION,
        ] = self.dfcalculation[PumpVariables.REQUIRED_SPEED_VARIATION]

        self.dfcalculation.loc[
            (self.dfcalculation[PumpVariables.SELECTED_MEASURE] == "Impeller")
            & (self.dfcalculation[PumpVariables.WORKING_PERCENT] > 0),
            PumpVariables.SELECTED_SPEED_VARIATION,
        ] = (
            self.dfcalculation.loc[
                self.dfcalculation[PumpVariables.WORKING_PERCENT] > 0,
                PumpVariables.REQUIRED_SPEED_VARIATION,
            ]
            .dropna()
            .max()
        )

        self.dfcalculation.loc[
            (self.dfcalculation[PumpVariables.WORKING_PERCENT] <= 0),
            PumpVariables.SELECTED_SPEED_VARIATION,
        ] = 0

    def __get_energy_columns(self):
        """
        Private method used in create_energy_calculation() method to create energy related columns
        in dfcalculation dataframe.
        """

        # calculate base case annual energy consumption
        self.dfcalculation[PumpVariables.BASE_CASE_ENERGY_CONSUMPTION] = (
            self.dfcalculation[PumpVariables.BASE_MOTOR_POWER]
            * self.dfcalculation[PumpVariables.WORKING_HOURS]
        )

        # calculate proposed case efficiency
        self.dfcalculation[PumpVariables.NEW_PUMP_EFFICIENCY] = self.dfcalculation[
            PumpVariables.OLD_PUMP_EFFICIENCY
        ]
        self.dfcalculation[PumpVariables.NEW_MOTOR_EFFICIENCY] = self.dfcalculation[
            PumpVariables.OLD_MOTOR_EFFICIENCY
        ]

        # calculate proposed case annual energy consumption
        eff_factor = (
            self.dfcalculation[PumpVariables.NEW_PUMP_EFFICIENCY]
            * self.dfcalculation[PumpVariables.NEW_MOTOR_EFFICIENCY]
        ) / (
            self.dfcalculation[PumpVariables.OLD_PUMP_EFFICIENCY]
            * self.dfcalculation[PumpVariables.OLD_MOTOR_EFFICIENCY]
        )

        self.dfcalculation[PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION] = (
            self.dfcalculation[PumpVariables.BASE_CASE_ENERGY_CONSUMPTION]
            * (self.dfcalculation[PumpVariables.SELECTED_SPEED_VARIATION] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        self.dfcalculation[PumpVariables.ANNUAL_ENERGY_SAVING] = (
            self.dfcalculation[PumpVariables.BASE_CASE_ENERGY_CONSUMPTION]
            - self.dfcalculation[PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION]
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
            self.dfcalculation[PumpVariables.BASE_CASE_ENERGY_CONSUMPTION]
            * emission_factor
        )

        self.dfcalculation[EmissionVariables.PROPOSED_CASE_EMISSION] = (
            self.dfcalculation[PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION]
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

    def create_energy_calculation(self, site: str):
        """
        - Create energy calculation dataframe for VSD and Impeller options.
        - Create summary dataframe for VSD and Impeller options.
        - Finally, renames the columns of all the dataframes from snake_case to Proper Case.
        """
        for option in ["Vsd", "Impeller"]:
            self.dfcalculation[PumpVariables.SELECTED_MEASURE] = option
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

        if self.df_summary["Vsd"][PumpVariables.BASE_CASE_ENERGY_CONSUMPTION] == 0:
            error_msg = (
                "Base case energy consumption is zero. Please check the input data."
            )
            raise CustomException(error_msg)

        self.logger.info("Energy calculation completed")

    def __summarize(self, dfenergy, site):
        """
        PRIVATE METHOD USED IN create_energy_calculation()

        Creates summary dataframe for VSDCalculation and ImpellerCalculation dataframe
        """
        columns = [
            PumpDesignDataVariables.EQUIPMENT_TAG,
            PumpDesignDataVariables.RATED_FLOWRATE,
            PumpVariables.SELECTED_SPEED_VARIATION,
            PumpVariables.BASE_CASE_ENERGY_CONSUMPTION,
            PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION,
            PumpVariables.ANNUAL_ENERGY_SAVING,
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

        df_summary[PumpVariables.SELECTED_SPEED_VARIATION] = (
            f"{dfenergy[PumpVariables.SELECTED_SPEED_VARIATION].max():.0%}"
            + " - "
            + f"{dfenergy[PumpVariables.SELECTED_SPEED_VARIATION].min():.0%}"
        )
        df_summary[PumpVariables.BASE_CASE_ENERGY_CONSUMPTION] = dfenergy[
            PumpVariables.BASE_CASE_ENERGY_CONSUMPTION
        ].sum()
        df_summary[PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION] = dfenergy[
            PumpVariables.PROPOSED_CASE_ENERGY_CONSUMPTION
        ].sum()
        df_summary[PumpVariables.ANNUAL_ENERGY_SAVING] = dfenergy[
            PumpVariables.ANNUAL_ENERGY_SAVING
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
            **self.pump_data.mandatory_columns,
            **self.pump_data.optional_columns,
            **self.pump_data.computed_columns,
            **self.pump_data.energy_columns,
            **self.pump_data.emission_columns,
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
                PumpVariables.ANNUAL_ENERGY_SAVING
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
                PumpVariables.ANNUAL_ENERGY_SAVING
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
                PumpVariables.ANNUAL_ENERGY_SAVING
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

    def write_to_excel(self):
        """
        Creates excel file based on the output folder, site and tag.
        Writes three dataframes to excel file.
        1. df_summary
        2. VSDCalculation
        3. ImpellerCalculation

        """
        try:
            output_folder = Path("src/data/output")
            output_folder.mkdir(parents=True, exist_ok=True)
            path = output_folder / "Output.xlsx"

            # Create a Pandas Excel writer using XlsxWriter as the engine.
            writer = pd.ExcelWriter(path, engine="xlsxwriter")

            # Write each DataFrame to a specific sheet
            self.df_summary.to_excel(writer, sheet_name="Summary")
            self.vsd_calculation.to_excel(writer, sheet_name="VSD Calculation")
            self.impeller_calculation.to_excel(
                writer, sheet_name="Impeller Calculation"
            )
            self.df_economics.to_excel(writer, sheet_name="Economics")

            # Save the writer (and thus the file)
            writer.close()

            # Optionally convert to PDF here if necessary

            self.logger.info(f"Excel file created at {path}")

        except Exception as e:
            self.logger.exception("Error in writing to excel.")
            # Handle or raise the exception as needed

    def process_pump(self):
        """
        Main method to run the pump analysis.
        """
        try:
            self.get_computed_columns()
            self.group_by_flowrate_percent()
            self.create_energy_calculation(site="UL")
            self.get_economics_summary()
            self.write_to_excel()
        except CustomException as e:
            self.logger.error(e)
            print(traceback.format_exc())
            raise CustomException(e) from e
        except Exception as e:
            self.logger.error(e)
            print(traceback.format_exc())
            raise CustomException(e) from e
