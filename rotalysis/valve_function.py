"""valve_function.py"""

import math

import pandas as pd

from utils import Databook

from .definitions import ValveCharacter


class ValveFunction:
    """This class contains static functions for valve calculations."""

    df_rated_cv: pd.DataFrame = Databook().get_dataframe(
        sheet_name="Valve", cell_range="Valve", first_col_as_index=True
    )

    @classmethod
    def get_linear_cv(cls, valve_size: str):
        """Get linear Cv based on valve size."""
        try:
            return cls.df_rated_cv.loc[valve_size, ValveCharacter.LINEAR]
        except KeyError as e:
            raise ValueError(
                f"Valve size '{valve_size}' not found or Linear Cv not available."
            ) from e

    @classmethod
    def get_equal_cv(cls, valve_size: str):
        """Get equal percentage Cv based on valve size."""
        try:
            return cls.df_rated_cv.loc[valve_size, ValveCharacter.EQUAL_PERCENTAGE]
        except KeyError as e:
            raise ValueError(
                f"Valve size '{valve_size}' not found or Equal Percentage Cv not available."
            ) from e

    @classmethod
    def get_rated_cv(cls, valve_size: str, valve_character: ValveCharacter):
        """Get rated Cv based on valve size and character."""
        if valve_character == ValveCharacter.LINEAR:
            return cls.get_linear_cv(valve_size)
        if valve_character == ValveCharacter.EQUAL_PERCENTAGE:
            return cls.get_equal_cv(valve_size)
        raise ValueError(f"Unsupported valve character: {valve_character}")

    @staticmethod
    def get_actual_cv(rated_cv, cv_opening: float, valve_character: ValveCharacter):
        """Calculate actual Cv based on opening and character."""
        if valve_character == ValveCharacter.LINEAR:
            return rated_cv * (cv_opening / 100)
        if valve_character == ValveCharacter.EQUAL_PERCENTAGE:
            return rated_cv * (cv_opening / 100) ** 3
        if valve_character == ValveCharacter.QUICK_OPENING:
            return rated_cv * math.sqrt(cv_opening / 100)

        raise ValueError(f"Unsupported valve character: {valve_character}")

    @staticmethod
    def get_pressure_drop(
        discharge_flowrate: float, cv: float, density: float
    ) -> float:
        """Calculate control valve pressure drop in bar."""
        cv = cv / 1.156  # Convert Cv to metric units if needed
        cv_pressure_drop = (discharge_flowrate / cv) ** 2 * (density / 1000)
        return cv_pressure_drop

    @staticmethod
    def cv_gas(
        w: float, p_in: float, p_out: float, t: float, z: float, mw: float, k: float
    ) -> float:
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
        p_in += 1.01325  # Convert to absolute pressure
        p_out += 1.01325
        x = (p_in - p_out) / p_in
        xt = 0.7
        xchoke = (k / 1.4) * xt
        xsize = min(x, xchoke)
        y = 1 - (xsize / (3 * xchoke))
        return (w / (94.8 * y * p_in)) * math.sqrt((t + 273.15) * z / (xsize * mw))
