""""
rotalysis.pump.pump
This module contains the class Pump, which represents a pump object.
"""

from typing import Dict, List, Optional, Tuple

import pandas as pd
import pint

ureg = pint.UnitRegistry(system="SI")


class Pump:
    """
    Pump class to represent a pump object.
    Follows SI units for all calculations.
    m, kg, s, J, W, Pa, N, etc.
    """

    def __init__(
        self,
        rated_head: float,
        rated_flow: float,
        density: float = 1000.0,
    ):
        """
        Initialize a Pump object.

        Args:
            rated_head (float): m
            rated_flow (float): m^3/s
            density (float, optional): kg/m^3. Defaults to 1000.0.
        """
        self.rated_head = rated_head
        self.rated_flow = rated_flow
        self.density = density

    def __repr__(self):
        return f"Pump(rated_head={self.rated_head}, rated_flow={self.rated_flow})"

    def get_sample_head_curve(self) -> pd.DataFrame:  # TODO: Implement this method
        """
        sample pump head curve equation

        H = aQ^2 + bQ + c
        a	-0.0006
        b	0.1394
        c	727

        """
        df = pd.DataFrame(columns=["flow_rate", "head"])
        return df

    def get_sample_efficiency_curve(
        self,
    ) -> pd.DataFrame:  # TODO: Implement this method
        """
        sample pump efficiency curve equation

        η = aQ^2 + bQ + c
        a = -0.0003
        b = 0.286
        c = 0
        """
        df = pd.DataFrame(columns=["flow_rate", "efficiency"])
        return df
