""""
src/components/design_stage/energy_savings_data.py
This module contains the energy savings data of the pump
"""

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from rotalysis.pump import Pump

from . import ids

# Global figure to maintain state across updates
PUMP_CURVE_FIG = go.Figure()


def create_bar_chart(x, y) -> go.Figure:
    # This might be a static figure that is only created once.
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y))
    fig.update_layout(
        title="Energy Savings",
        xaxis_title="Flow Spread Pattern",
        yaxis_title="Operating Hours",
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


def export_container(id: str):
    return html.Div(
        [
            html.Button(id=ids.GENERATE_GRAPH_BUTTON, children="Generate Graph"),
            dcc.Graph(
                id=ids.ENERGY_SAVINGS_GRAPH,
                figure={},
            ),
        ],
        id=id,
    )


def register_callbacks():
    @callback(
        Output(ids.ENERGY_SAVINGS_GRAPH, "figure"),
        [
            Input(ids.PUMP_CURVE_DATA, "rowData"),
            Input(ids.SYSTEM_CURVE_DATA, "rowData"),
            Input(ids.EFFICIENCY_CURVE_DATA, "rowData"),
        ],
        prevent_initial_call=True,
    )
    def update_all_graphs(pump_data, system_data, efficiency_data):
        global PUMP_CURVE_FIG

        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        PUMP_CURVE_FIG = update_figure_with_curve(pump_data, PUMP_CURVE_FIG, "pump")
        PUMP_CURVE_FIG = update_figure_with_curve(system_data, PUMP_CURVE_FIG, "system")
        PUMP_CURVE_FIG = update_figure_with_curve(efficiency_data, PUMP_CURVE_FIG, "efficiency")

        return PUMP_CURVE_FIG
