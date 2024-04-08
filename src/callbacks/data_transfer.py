"""
callbacks.data_transfer
This module contains the callbacks for data transfer (uploading and downloading files).
"""

from typing import Dict, Tuple

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

from components import ids


def register_callbacks(app: Dash):
    register_upload_callbacks(app)
    register_download_callbacks(app)


def register_upload_callbacks(app: Dash):
    @app.callback(
        [
            Output(ids.UPLOAD_OUTPUT, "children"),
            Output(ids.STORE_DATA, "data"),
            Output(ids.UPLOAD_DATA, "style"),
        ],
        Input(ids.UPLOAD_DATA, "contents"),
        State(ids.UPLOAD_DATA, "filename"),
        prevent_initial_call=True,
    )
    def store_uploaded_file(
        contents: str, filename: str
    ) -> Tuple[html.Div, Dict[str, str], Dict[str, str]]:
        if contents is not None:
            data = {"filename": filename, "contents": contents}
            upload_response = html.Div(html.H5(f"File {filename} has been uploaded."))
            style = {"display": "none"}
        else:
            data = {"filename": "", "contents": ""}
            upload_response = html.Div(html.H5("No file has been uploaded."))
            style = {"display": "block"}

        return (upload_response, data, style)


def register_download_callbacks(app: Dash):

    @app.callback(
        Output(ids.DOWNLOAD_OUTPUT, "data"),
        Input(ids.DOWNLOAD_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def download_result(n_clicks: int):
        if n_clicks is None:
            return None
        return dcc.send_file("src/data/output/Output.xlsx")
