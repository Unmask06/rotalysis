"""
pages/calculation.py - Calculation page for the Rotalysis app.
"""

import base64
import io
from typing import Dict

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html, no_update

from components.calculation import button, ids, upload_file


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


upload_file.register_callbacks()
button.register_callbacks()
