"""Upload file component."""

from typing import Dict, Tuple

import dash
from dash import Input, Output, State, dcc, html, callback

from . import ids


def render() -> html.Div:

    return html.Div(
        [
            dcc.Loading(
                dcc.Upload(
                    id=ids.UPLOAD_DATA,
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    multiple=False,
                )
            ),
            dcc.Store(id=ids.STORE_DATA, data={}),
            html.Div(id=ids.UPLOAD_OUTPUT, children="Upload file to see the result"),
        ]
    )


def register_callbacks():

    @callback(
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
