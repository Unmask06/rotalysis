""""
src/components/design_stage/energy_savings_data.py
This module contains the energy savings data of the pump
"""

import dash
import pandas as pd
import plotly.graph_objects as go
from agility.skeleton.custom_components import CheckboxCustom
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from rotalysis.pump import Pump

from . import ids


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


graph_checkbox = CheckboxCustom(
    options=[
        "pump",
        "system",
        "efficiency",
    ],
    value=["pump"],
    label="Select Curves to Display",
    help_text="Select the curves you want to display on the graph.",
    error_message="",
)

test_div = html.Div(id=ids.TEST_DIV)


def export_container(id: str):
    return html.Div(
        [
            html.Button(id=ids.GENERATE_GRAPH_BUTTON, children="Generate Graph"),
            graph_checkbox.layout,
            dcc.Graph(
                id=ids.ENERGY_SAVINGS_GRAPH,
                figure={},
            ),
            test_div,
        ],
        id=id,
    )


def register_callbacks():
    @callback(
        Output(ids.TEST_DIV, "children"),
        [Input(ids.GENERATE_GRAPH_BUTTON, "n_clicks")],
        [State(ids.ENERGY_SAVINGS_GRAPH, "figure")],
        prevent_initial_call=True,
    )
    def check_figure(n_clicks, figure):
        if n_clicks == 0:
            raise dash.exceptions.PreventUpdate
        return html.Div(f"Figure: {figure}")

    # callback to get the selected curves
    @callback(
        Output(ids.ENERGY_SAVINGS_GRAPH, "figure"),
        [Input(graph_checkbox.id, "value")],
        [
            State(ids.PUMP_CURVE_DATA, "rowData"),
            State(ids.SYSTEM_CURVE_DATA, "rowData"),
            State(ids.EFFICIENCY_CURVE_DATA, "rowData"),
        ],
        prevent_initial_call=True,
    )
    def update_graph(curve_types, pump_data, system_data, efficiency_data):
        fig = go.Figure()
        if "pump" in curve_types:
            fig = update_figure_with_curve(pump_data, fig, "pump")
        if "system" in curve_types:
            fig = update_figure_with_curve(system_data, fig, "system")
        if "efficiency" in curve_types:
            fig = update_figure_with_curve(efficiency_data, fig, "efficiency")
        return fig
