import dash
import dash_bootstrap_components as dbc

from .sidebar import create_sidebar


def create_layout(app) -> dbc.Container:
    return dbc.Container(
        children=[
            dbc.Row(create_sidebar(app.title)),
            dbc.Row([dash.page_container]),
        ],
        fluid=True,
    )
