"""app.py - Main file for the Rotalyis app."""

import dash_bootstrap_components as dbc
from dash import Dash

# from callbacks import calculation, design_stage
# from components.calculation import upload_file
from components.common.layout import create_layout

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.15.4/js/all.js"
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
)

app.title = "Rotalysis"

app.layout = create_layout(app)


if __name__ == "__main__":
    app.run(debug=True, port="80")
