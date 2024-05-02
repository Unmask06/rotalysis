""""
src/components/design_stage/energy_savings_data.py
This module contains the energy savings data of the pump
"""

import pandas as pd
import plotly.graph_objects as go
from agility.skeleton.custom_components import CheckboxCustom, ContainerCustom
from dash import callback, dcc
from dash.dependencies import Input, Output, State

from rotalysis.pump import Pump

from . import ids
from .pump_design_data import efficiency_curve_grid, pump_curve_grid, system_curve_grid


def create_bar_chart(fig: go.Figure, x, y) -> go.Figure:
    fig.add_trace(go.Bar(x=x, y=y, yaxis="y3"))
    fig.update_layout(
        yaxis3=dict(
            title="Operating Hours",
            overlaying="y",
            side="right",
            showgrid=False,
            showline=True,
            showticklabels=True,
            zeroline=False,
            position=0.95,
        ),
    )
    return fig


def update_figure_with_curve(data, fig, curve_type):
    """General function to update figure with different types of curves."""
    df = pd.DataFrame(data)
    pump = Pump()

    if curve_type == "pump":
        return pump.add_pump_curve(
            flowrates=df["flow_rate"], pump_heads=df["pump_head"], fig=fig
        )
    if curve_type == "system":
        return pump.add_system_curve(
            flowrates=df["flow_rate"], system_heads=df["system_head"], fig=fig
        )
    if curve_type == "efficiency":
        return pump.add_efficiency_curve(
            flowrates=df["flow_rate"], efficiencies=df["efficiency"], fig=fig
        )


graph_checkbox = CheckboxCustom(
    options=["pump", "system", "efficiency", "flow_spread"],
    value=[],
    label="Select Curves to Display",
    help_text="Select the curves you want to display on the graph.",
    error_message="",
)


def export_container():
    return ContainerCustom(
        [
            graph_checkbox.layout,
            dcc.Graph(
                id=ids.ENERGY_SAVINGS_GRAPH,
                figure={},
                style={"display": "none"},
            ),
        ],
    ).layout


def register_callbacks():
    # callback to get the selected curves
    @callback(
        [
            Output(ids.ENERGY_SAVINGS_GRAPH, "figure"),
            Output(ids.ENERGY_SAVINGS_GRAPH, "style"),
        ],
        [Input(graph_checkbox.id, "value")],
        [
            State(pump_curve_grid.id, "rowData"),
            State(system_curve_grid.id, "rowData"),
            State(efficiency_curve_grid.id, "rowData"),
            State(ids.FLOW_SPREAD_TABLE, "rowData"),
        ],
        prevent_initial_call=True,
    )
    def update_graph(
        curve_types, pump_data, system_data, efficiency_data, flow_spread_data
    ):
        fig = go.Figure()
        if "pump" in curve_types:
            fig = update_figure_with_curve(pump_data, fig, "pump")
        if "system" in curve_types:
            fig = update_figure_with_curve(system_data, fig, "system")
        if "efficiency" in curve_types:
            fig = update_figure_with_curve(efficiency_data, fig, "efficiency")
        if "flow_spread" in curve_types:
            df = pd.DataFrame(flow_spread_data)
            fig = create_bar_chart(
                fig, df["rated_flow_percentage"], df["operated_hours"]
            )
        return fig, {"display": "block"}
