import dash
from dash import Dash, callback, html, Input, Output, State

from components.design_stage import ids

def design_stage_callbacks(app: Dash):
    @app.callback(
        Output("percentage-table", "data"),
        Input(ids.NORMAL_HOURS_BUTTON, "n_clicks"),
        State("percentage-table", "data"),
    )
    def update_total(_, rows):
        print("Updating total")
        if not rows:
            print("No rows")
            raise dash.exceptions.PreventUpdate

    #     for row in rows:
    #         row["Total"] = sum(row[col["id"]] for col in percentage_columns)
    #     return rows