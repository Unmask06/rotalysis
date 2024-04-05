"""Upload file component."""

from dash import dcc, html


def render() -> html.Div:
    return html.Div(
        [
            html.H1("Upload File"),
            dcc.Upload(
                id="upload-data",
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
            html.Div(id="output-data-upload", children="Upload file to see the result"),
        ]
    )
