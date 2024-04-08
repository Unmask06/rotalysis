"""Upload file component."""

from dash import dcc, html

from . import ids


def render() -> html.Div:
    return html.Div(
        [
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
            ),
            dcc.Store(id=ids.STORE_DATA, data={}),
            html.Div(id=ids.UPLOAD_OUTPUT, children="Upload file to see the result"),
        ]
    )
