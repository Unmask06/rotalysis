from typing import Optional

import numpy as np
import pandas as pd

from rotalysis.definitions import PumpCalculationMethod, PumpControlStrategy
from rotalysis.definitions import PumpVariables as pumpvar
from rotalysis.pump import Pump, PumpFunction
from rotalysis.pump import curve_generator as cg
from rotalysis.pump.curve_generator import QuadCoeffs


class EnergySavingsCalculator:
    """
    This class is used to calculate the energy savings in a pump by changing the speed of the pump.

    Attributes:
        pump (Pump): Pump object.
        system_curve_coeffs (QuadCoeffs): Coefficients of the system curve.
        pump_curve_coeffs (QuadCoeffs): Coefficients of the pump curve.
        efficiency_curve_coeffs (QuadCoeffs): Coefficients of the efficiency curve.

    """

    defaults: dict

    def __init__(
        self,
        pump: Pump,
        strategy: PumpControlStrategy = PumpControlStrategy.VARIABLE_SPEED_DRIVE,
        calculation_mode: PumpCalculationMethod = PumpCalculationMethod.TWO_POINT_METHOD,
        system_curve_coeffs: Optional[QuadCoeffs] = None,
        pump_curve_coeffs: Optional[QuadCoeffs] = None,
        efficiency_curve_coeffs: Optional[QuadCoeffs] = None,
        working_percent: Optional[pd.DataFrame] = None,
        dfcalculation: Optional[pd.DataFrame] = None,
    ):
        self.pump = pump
        self.strategy = strategy
        self.calculation_mode = calculation_mode
        self.system_curve_coeffs = system_curve_coeffs
        self.pump_curve_coeffs = pump_curve_coeffs
        self.efficiency_curve_coeffs = efficiency_curve_coeffs
        self.working_percent = working_percent
        self.dfcalculation = dfcalculation
        self.__set_defaults()
        self.__validate_input()

    def __set_defaults(self):
        """
        Private method to set default values to the attributes.
        """
        self.defaults: dict = {pumpvar.OLD_MOTOR_EFFICIENCY: 0.9}

    def __validate_input(self):
        """
        Private method to validate the input data.
        """
        if self.calculation_mode == PumpCalculationMethod.HISTORIAN_DATA:
            if self.dfcalculation is None:
                raise ValueError("dfcalculation is missing.")
            if not set(self.dfcalculation.columns).issuperset(
                {
                    pumpvar.FLOWRATE_PERCENT,
                    pumpvar.DISCHARGE_FLOWRATE,
                    pumpvar.DIFFERENTIAL_PRESSURE,
                    pumpvar.REQUIRED_DIFFERENTIAL_PRESSURE,
                    pumpvar.OLD_PUMP_EFFICIENCY,
                    pumpvar.BASE_HYDRAULIC_POWER,
                    pumpvar.REQUIRED_SPEED_VARIATION,
                    pumpvar.WORKING_PERCENT,
                    pumpvar.BASE_MOTOR_POWER,
                }
            ):
                raise ValueError(
                    "dfcalculation must contain the required columns: "
                    "FLOWRATE_PERCENT, DISCHARGE_FLOWRATE, DIFFERENTIAL_PRESSURE, "
                    "REQUIRED_DIFFERENTIAL_PRESSURE, OLD_PUMP_EFFICIENCY, BASE_HYDRAULIC_POWER, "
                    "REQUIRED_SPEED_VARIATION, WORKING_PERCENT, BASE_MOTOR_POWER."
                )

    def get_dfcalculation(
        self,
    ):
        """
        Generates a calculation table based on the pump design data.

        """

        if (
            self.calculation_mode == PumpCalculationMethod.HISTORIAN_DATA
            and self.dfcalculation is not None
        ):
            return self.dfcalculation

        if self.calculation_mode != PumpCalculationMethod.HISTORIAN_DATA:
            if self.system_curve_coeffs is None:
                raise ValueError("System curve coefficients are missing.")
            if self.pump_curve_coeffs is None:
                raise ValueError("Pump curve coefficients are missing.")
            if self.efficiency_curve_coeffs is None:
                raise ValueError("Efficiency curve coefficients are missing.")

        flowrate_percent = np.linspace(0, 1.0, 11)
        discharge_flowrates = [self.pump.rated_flow * flow for flow in flowrate_percent]
        differential_pressures = [
            cg.get_y_from_curve(flow, self.pump_curve_coeffs)
            for flow in discharge_flowrates
        ]
        required_differential_pressures = [
            cg.get_y_from_curve(flow, self.system_curve_coeffs)
            for flow in discharge_flowrates
        ]
        old_efficiencies = [
            cg.get_y_from_curve(flow, self.efficiency_curve_coeffs)
            for flow in discharge_flowrates
        ]

        df = pd.DataFrame(
            {
                pumpvar.FLOWRATE_PERCENT: 100 * flowrate_percent,
                pumpvar.DISCHARGE_FLOWRATE: discharge_flowrates,
                pumpvar.DIFFERENTIAL_PRESSURE: differential_pressures,
                pumpvar.REQUIRED_DIFFERENTIAL_PRESSURE: required_differential_pressures,
                pumpvar.OLD_PUMP_EFFICIENCY: old_efficiencies,
            }
        )

        df[pumpvar.BASE_HYDRAULIC_POWER] = PumpFunction.get_base_hydraulic_power(
            df[pumpvar.DISCHARGE_FLOWRATE], df[pumpvar.DIFFERENTIAL_PRESSURE]
        )

        df[pumpvar.REQUIRED_SPEED_VARIATION] = PumpFunction.get_speed_variation(
            df[pumpvar.DIFFERENTIAL_PRESSURE],
            df[pumpvar.REQUIRED_DIFFERENTIAL_PRESSURE],
        )

        df[pumpvar.BASE_MOTOR_POWER] = (
            df[pumpvar.BASE_HYDRAULIC_POWER]
            / self.defaults[pumpvar.OLD_MOTOR_EFFICIENCY]
        )

        return df

    def _select_speed_reduction(self):
        """
        Private method used in create_energy_calculation() method
            to select the speed reduction based on the options
        """
        df = self.get_dfcalculation()
        # self.working_percent has flowrate and weorking percent. assign the working percent to df based on the flowrate
        if self.working_percent is not None:
            df = pd.merge(
                df, self.working_percent, on=pumpvar.FLOWRATE_PERCENT, how="left"
            )
            df[pumpvar.WORKING_PERCENT] = df[pumpvar.WORKING_PERCENT].fillna(0)

        if self.strategy == PumpControlStrategy.VARIABLE_SPEED_DRIVE:

            df[pumpvar.SELECTED_SPEED_VARIATION] = df[pumpvar.REQUIRED_SPEED_VARIATION]

        if self.strategy == PumpControlStrategy.DISCHARGE_VALVE_THROTTLING:
            df.loc[
                df[pumpvar.WORKING_PERCENT] > 0,
                pumpvar.SELECTED_SPEED_VARIATION,
            ] = (
                df.loc[
                    df[pumpvar.WORKING_PERCENT] > 0,
                    pumpvar.REQUIRED_SPEED_VARIATION,
                ]
                .dropna()
                .max()
            )

        df.loc[
            (df[pumpvar.WORKING_PERCENT] <= 0),
            pumpvar.SELECTED_SPEED_VARIATION,
        ] = 0

        return df

    def __get_energy_columns(self, df):
        """
        Private method used in create_energy_calculation() method to create energy related columns
        in dfcalculation dataframe.
        """

        # calculate base case annual energy consumption
        df[pumpvar.WORKING_HOURS] = df[pumpvar.WORKING_PERCENT] * 8760

        df[pumpvar.BASE_CASE_ENERGY_CONSUMPTION] = (
            df[pumpvar.BASE_MOTOR_POWER] * df[pumpvar.WORKING_HOURS]
        )

        # calculate proposed case efficiency
        df[pumpvar.NEW_PUMP_EFFICIENCY] = df[pumpvar.OLD_PUMP_EFFICIENCY]

        # calculate proposed case annual energy consumption
        eff_factor = (
            df[pumpvar.NEW_PUMP_EFFICIENCY]
            * self.defaults[pumpvar.OLD_MOTOR_EFFICIENCY]
        ) / (
            df[pumpvar.OLD_PUMP_EFFICIENCY]
            * self.defaults[pumpvar.OLD_MOTOR_EFFICIENCY]
        )

        df[pumpvar.PROPOSED_CASE_ENERGY_CONSUMPTION] = (
            df[pumpvar.BASE_CASE_ENERGY_CONSUMPTION]
            * (df[pumpvar.SELECTED_SPEED_VARIATION] ** 3)
            * eff_factor
        )

        # calculate annual energy savings
        df[pumpvar.ANNUAL_ENERGY_SAVING] = (
            df[pumpvar.BASE_CASE_ENERGY_CONSUMPTION]
            - df[pumpvar.PROPOSED_CASE_ENERGY_CONSUMPTION]
        )
        
        df = df.loc[df[pumpvar.WORKING_PERCENT] > 0]

        return df

    @property
    def energy_savings(self):
        """
        Returns the annual energy savings in the pump.
        """
        df = self._select_speed_reduction()
        return self.__get_energy_columns(df)
