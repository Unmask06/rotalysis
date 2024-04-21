""""
rotalysis.pump.pump
This module contains the class Pump, which represents a pump object.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pint
from plotly import graph_objects as go

from . import curve_generator as cg

ureg = pint.UnitRegistry(system="SI")


class Pump:
    """
    Pump class to represent a pump object.
    Follows SI units for all calculations.
    m, kg, s, J, W, Pa, N, etc.
    """

    sample_rated_flow: float

    def __init__(
        self,
        rated_head: Optional[float] = None,
        rated_flow: Optional[float] = None,
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

    @property
    def sample_pump_curve(self) -> pd.DataFrame:
        """
        Returns a sample pump curve as a pandas DataFrame.

        The pump curve includes flow rate, head, and efficiency values
        calculated based on the given coefficients.

        Returns:
            pd.DataFrame: A DataFrame containing the pump curve data.
                Columns: 'flow_rate', 'head', 'efficiency'
        """
        self.sample_rated_flow = 638  # m^3/h
        flowrates = np.linspace(0, self.sample_rated_flow * 1.3, 10)

        # Head Curve Generation
        head_coefficents = {"a": -0.0006, "b": -0.1382, "c": 727}
        hea_quadratic_eq = cg.get_quadratic_equation(**head_coefficents)
        pump_heads = [hea_quadratic_eq(q) for q in flowrates]

        # Efficiency Curve Generation
        efficiency_coefficents = {"a": -0.0003, "b": 0.286, "c": 0}
        eff_quadratic_eq = cg.get_quadratic_equation(**efficiency_coefficents)
        efficiencies = [eff_quadratic_eq(q) for q in flowrates]

        # Sytem Curve Generation
        system_coefficents = {"a": 0.00093, "b": 0, "c": 0}
        sys_quadratic_eq = cg.get_quadratic_equation(**system_coefficents)
        system_heads = [sys_quadratic_eq(q) for q in flowrates]

        return pd.DataFrame(
            {
                "flow_rate": flowrates,
                "pump_head": pump_heads,
                "efficiency": efficiencies,
                "system_head": system_heads,
            }
        )

    def add_pump_curve(self, flowrates, pump_heads, fig: go.Figure) -> go.Figure:
        fig.add_trace(
            go.Scatter(
                x=flowrates,
                y=pump_heads,
                mode="lines",
                name="Head",
            )
        )
        return fig

    def add_efficiency_curve(
        self, flowrates, efficiencies, fig: go.Figure
    ) -> go.Figure:
        fig.add_trace(
            go.Scatter(
                x=flowrates,
                y=efficiencies,
                mode="lines",
                name="Efficiency",
                yaxis="y2",
                line=dict(color="red", smoothing=1, shape="spline"),
            )
        )

        # Ensure the secondary y-axis is configured properly within this method
        fig.update_layout(
            yaxis2=dict(
                title="Efficiency (%)",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                overlaying="y",
                side="right",
                range=[0, 100],
            )
        )
        return fig

    def add_system_curve(self, flowrates, system_heads, fig: go.Figure) -> go.Figure:
        fig.add_trace(
            go.Scatter(
                x=flowrates,
                y=system_heads,
                mode="lines",
                name="System Head",
            )
        )
        return fig
