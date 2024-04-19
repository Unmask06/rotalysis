""""
src/components/design_stage/energy_savings_data.py
This module contains the energy savings data of the pump
"""

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from . import ids


def create_bar_chart(x, y) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y))
    fig.update_layout(
        title="Energy Savings",
        xaxis_title="Flow Spread Pattern",
        yaxis_title="Operating Hours",
    )
    return fig


def export_container(id: str):
    return html.Div(
        [
            html.Button(id=ids.GENERATE_GRAPH_BUTTON, children="Generate Graph"),
            dcc.Graph(
                id=ids.ENERGY_SAVINGS_GRAPH, figure={}, style={"display": "none"}
            ),
        ],
        id=id,
    )


def register_callbacks():

    @callback(
        [
            Output(ids.ENERGY_SAVINGS_GRAPH, "figure"),
            Output(ids.ENERGY_SAVINGS_GRAPH, "style"),
        ],
        [Input(ids.GENERATE_GRAPH_BUTTON, "n_clicks")],
        [State(ids.FLOW_SPREAD_TABLE, "rowData")],
        prevent_initial_call=True,
    )
    def update_graph(n_clicks, flow_spread_data):
        if n_clicks:
            df = pd.DataFrame(flow_spread_data)
            df = df.drop(columns=["Total"])
            x = df.columns.tolist()
            y = df.loc[0].values
            return create_bar_chart(x, y), {"display": "block"}
        return dash.no_update, dash.no_update
