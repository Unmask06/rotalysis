"""app.py - Main file for the Rotalyis app."""

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from callbacks import data_transfer,process_pump

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Rotalysis"

side_bar = dbc.Nav(
    [
        dbc.NavLink(
            [html.Div(page["name"], className="sidebar-text")],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=False,
    pills=True,
)


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1("Rotalysis", className="display-3"), xs=4, md=4, lg=4, xl=4
                ),
                dbc.Col(
                    [side_bar], xs=8, md=8, lg=8, xl=8, style={"text-align": "right"}
                ),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [dash.page_container],
                ),
            ]
        ),
    ],
    fluid=True,
)


app.layout = layout
data_transfer.register_callbacks(app)
process_pump.register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True, port="80")
