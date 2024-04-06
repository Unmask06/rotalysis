"""
callbacks.data_transfer
This module contains the callbacks for data transfer (uploading and downloading files).
"""

import base64
import io
from typing import Dict, Tuple

import pandas as pd
from dash import Dash, html
from dash.dependencies import Input, Output, State

from components import ids
from rotalysis.definitions import InputSheetNames





def register_callbacks(app: Dash):
    register_upload_callbacks(app)


def register_upload_callbacks(app: Dash):
    @app.callback(
        Output(ids.UPLOAD_OUTPUT, "children"),
        Output(ids.STORE_DATA, "data"),
        Input(ids.UPLOAD_DATA, "contents"),
        State(ids.UPLOAD_DATA, "filename"),
    )
    def store_uploaded_file(
        contents: str, filename: str
    ) -> Tuple[html.Div, Dict[str, str]]:
        if contents is not None:
            data = {"filename": filename, "contents": contents}
            upload_response = html.Div(html.H5(f"File {filename} has been uploaded."))
        else:
            data = {"filename": "", "contents": ""}
            upload_response = html.Div(html.H5(f"No file has been uploaded."))

        return (upload_response, data)

