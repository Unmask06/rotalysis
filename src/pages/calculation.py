"""
pages/calculation.py - Calculation page for the Rotalysis app.
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components import ids, upload_file

dash.register_page(__name__)


def layout():
    return dbc.Container(
        [
            html.P("This is the calculation page."),
            upload_file.render(),
            html.Button("Process Pump", id=ids.BUTTON_PROCESS_PUMP),
            html.Div(
                id=ids.OUTPUT_PROCESS_PUMP, children="Process pump to see the result"
            ),
            dcc.Download(id=ids.DOWNLOAD_OUTPUT),
        ]
    )
