"""
callbacks.data_transfer
This module contains the callbacks for data transfer (uploading and downloading files).
"""

from dash import Dash, html
from dash.dependencies import Input, Output, State


def register_callbacks(app: Dash):
    register_upload_callbacks(app)


def register_upload_callbacks(app: Dash):
    @app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )
    def update_output(contents, filename):
        if contents is not None:
            return html.Div([html.H5(f"Filename: {filename}"), html.H6(contents)])
        return "No file uploaded."
