import sys

sys.path.append("..")
import math

from utils import Databook


class ValveCharacter:
    LINEAR = "Linear"
    EQUAL_PERCENTAGE = "Equal Percentage"
    QUICK_OPENING = "Quick Opening"


class ValveFunction:
    df_rated_cv = Databook().get_dataframe(
        sheet_name="Valve", cell_range="Valve", first_col_as_index=True
    )

    @classmethod
    def get_linear_cv(cls, valve_size):
        return cls.df_rated_cv.loc[valve_size, ValveCharacter.LINEAR]

    @classmethod
    def get_equal_cv(cls, valve_size):
        return cls.df_rated_cv.loc[valve_size, ValveCharacter.EQUAL_PERCENTAGE]

    @classmethod
    def get_rated_cv(cls, valve_size, valve_character: ValveCharacter):
        if valve_character == ValveCharacter.LINEAR:
            rated_cv = cls.get_linear_cv(valve_size)
        elif valve_character == ValveCharacter.EQUAL_PERCENTAGE:
            rated_cv = cls.get_equal_cv(valve_size)
        return rated_cv  # type: ignore

    @staticmethod
    def get_actual_cv(rated_cv, cv_opening, valve_character: ValveCharacter):
        if valve_character == ValveCharacter.LINEAR:
            actual_cv = rated_cv * (cv_opening / 100)
        elif valve_character == ValveCharacter.EQUAL_PERCENTAGE:
            actual_cv = rated_cv * (cv_opening / 100) ** 3
        elif valve_character == ValveCharacter.QUICK_OPENING:
            actual_cv = rated_cv * (cv_opening / 100) ** 0.5
        return actual_cv  # type: ignore

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

    @staticmethod
    def CVgas(W, Pin, Pout, T, Z, MW, k):
        """
        Args:
            W (float): Mass flow rate in kg/hr
            Pin (float): Inlet pressure in barg
            Pout (float): Outlet pressure in barg
            T (float): Temperature in degC
            Z (float): Compressibility factor
            MW (float): Molecular weight in kg/kmol
            k (float): Specific heat ratio

            Returns:
            float: Control valve pressure drop in bar.
        """

        Pin = Pin + 1.01325
        Pout = Pout + 1.01325

        x = (Pin - Pout) / Pin
        xt = 0.7
        xchoke = (k / 1.4) * xt
        xsize = min(x, xchoke)

        Y = 1 - (xsize / (3 * xchoke))

        return (W / (94.8 * Y * Pin)) * math.sqrt((T + 273.15) * Z / (xsize * MW))
