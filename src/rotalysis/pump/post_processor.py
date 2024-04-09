"""
src/rotalysis/pump/post_processor.py
This module responsible for generating the graphs and figures for the pump data.
Also, formatting the data for the pump data.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from rotalysis import definitions as defs

from .pump import Pump


class PumpReporter:
    """
    A class that generates a report for pump analysis.

    Attributes:
        pump (Pump): The pump object containing the analysis results.
        vsd_calc (VSDCalculation): The VSD calculation object.
        imp_trim_calc (ImpellerCalculation): The impeller calculation object.
    """

    energy_savings_graph: go.Figure

    def __init__(self, pump: Pump) -> None:
        if pump.df_summary is None:
            raise ValueError(
                "Please run the pump analysis first before generating the report"
            )
        self.pump = pump
        self.vsd_calc = pump.vsd_calculation
        self.imp_trim_calc = pump.impeller_calculation

    def generate_energy_savings_graph(self) -> None:

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=self.vsd_calc[defs.ComputedVariables.FLOWRATE_PERCENT],
                y=self.vsd_calc[defs.ComputedVariables.WORKING_PERCENT],
                name="Flowrate %",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=self.imp_trim_calc[defs.ComputedVariables.FLOWRATE_PERCENT],
                y=self.imp_trim_calc[defs.ComputedVariables.ANNUAL_ENERGY_SAVING],
                mode="lines+markers",
                line_shape="spline",
                name="Annual Energy Saving (Impeller Trim)",
            ),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=self.vsd_calc[defs.ComputedVariables.FLOWRATE_PERCENT],
                y=self.vsd_calc[defs.ComputedVariables.ANNUAL_ENERGY_SAVING],
                mode="lines",
                line_shape="spline",
                name="Annual Energy Saving (VSD)",
            ),
            secondary_y=True,
        )

        fig.update_layout(
            title="Energy Savings upon implementing the VSD and Impeller Trim",
            xaxis_title="% of Rated Flowrate",
            yaxis_title="Working %",
            yaxis2={
                "title": "Annual Energy Saving (MWh)",
                "titlefont": {"color": "blue"},
                "tickfont": {"color": "blue"},
            },
        )

        self.energy_savings_graph = fig

    def generate_report(self) -> None:
        self.generate_energy_savings_graph()
        print("Report generated successfully")
