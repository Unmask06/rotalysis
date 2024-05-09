""""
rotalysis.pump.pump
This module contains the class Pump, which represents a pump object.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pint
from plotly import graph_objects as go

from rotalysis.fluid import Fluid

from . import curve_generator as cg
from .curve_generator import QuadCoeffs

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
        fluid: Fluid = Fluid(),
    ):
        """
        Initialize a Pump object.

        Args:
            rated_head (float): m
            rated_flow (float): m^3/s
            fluid (Fluid, optional): Fluid object. Defaults to Water.
        """
        self.rated_head = rated_head
        self.rated_flow = rated_flow
        self.fluid = fluid

    def __repr__(self):
        return f"Pump(rated_head={self.rated_head}, rated_flow={self.rated_flow}, fluid={self.fluid})"

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
        head_coefficents = QuadCoeffs(a=-0.0006, b=-0.1382, c=727)

        pump_heads = [cg.get_y_from_curve(q, head_coefficents) for q in flowrates]

        # Efficiency Curve Generation
        efficiency_coefficents = QuadCoeffs(a=-0.0003, b=0.286, c=0)
        efficiencies = [
            cg.get_y_from_curve(q, efficiency_coefficents) for q in flowrates
        ]

        # Sytem Curve Generation
        system_coefficients = QuadCoeffs(a=0.00093, b=0, c=0)
        system_heads = [cg.get_y_from_curve(q, system_coefficients) for q in flowrates]

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
