"""
pages/calculation.py - Calculation page for the Rotalysis app.
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.calculation import ids
from components.calculation import upload_file

dash.register_page(__name__)


def layout():
    return dbc.Container(
        [
            html.H3("Calculation Page"),
            upload_file.render(),
            html.Button("Process Pump", id=ids.BUTTON_PROCESS_PUMP),
            dcc.Loading(
                id=ids.LOADING_PROCESS_PUMP,
                type="default",
                children=[
                    html.Div(
                        id=ids.OUTPUT_PROCESS_PUMP,
                        children="Process pump to see the result",
                    )
                ],
            ),
            dbc.Container(
                [
                    dcc.Download(id=ids.DOWNLOAD_OUTPUT),
                    dbc.Button(
                        id=ids.DOWNLOAD_BUTTON,
                        children=[
                            html.I(className="fa-regular fa-circle-down"),
                            "Download the result",
                        ],
                    ),
                    html.Div(id=ids.OUTPUT_SUMMARY_TABLE),
                    dcc.Graph(id=ids.GRAPH_REPORT_ENERGY_SAVINGS),
                ],
                id=ids.OUTPUT_CONTAINER,
                style={"display": "none"},
            ),
        ]
    )
