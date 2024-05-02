import dash
import dash_ag_grid as dag
import pandas as pd
from agility.skeleton.custom_components import (
    ButtonCustom,
    ContainerCustom,
    DisplayField,
    DropdownCustom,
)
from dash import callback, html
from dash.dependencies import Input, Output, State

from . import ids

# Component creation -----------------------------------------------------------

flow_spread_df: pd.DataFrame = pd.DataFrame(
    columns=["rated_flow_percentage", "operated_hours"],
    data=[
        ["30%", 0],
        ["40%", 0],
        ["50%", 0],
        ["60%", 0],
        ["70%", 0],
        ["80%", 0],
        ["90%", 0],
        ["100%", 0],
    ],
)


flow_spread_dropdown = DropdownCustom(
    label="Flow Spread Pattern",
    options=[
        {"label": "Constant", "value": "constant"},
        {"label": "Variable", "value": "variable"},
    ],
)

flow_spread_table = dag.AgGrid(
    id=ids.FLOW_SPREAD_TABLE,
    columnDefs=[
        {
            "headerName": "Rated Flow Percentage",
            "field": "rated_flow_percentage",
            "editable": False,
        },
        {"headerName": "Operated Hours (hrs/day)", "field": "operated_hours"},
    ],
    defaultColDef={"resizable": True, "editable": True},
    rowData=flow_spread_df.to_dict("records"),
    className="ag-theme-alpine",
    style={"width": "50%"},
)

flow_spread_total = DisplayField(
    label="Total Hours", value=str(0), addon_text="hrs/day"
)

normalize_button = ButtonCustom(label="Normalize Hours")


def export_container() -> html.Div:
    return ContainerCustom(
        [
            flow_spread_dropdown.layout,
            flow_spread_table,
            flow_spread_total.layout,
            normalize_button.layout,
        ]
    ).layout


# Callbacks Resgistration ------------------------------------------------------


def register_callbacks():
    # get total hours
    @callback(
        Output(flow_spread_total.value_id, "children"),
        [
            Input(ids.FLOW_SPREAD_TABLE, "cellValueChanged"),
            Input(ids.FLOW_SPREAD_TABLE, "rowData"),
        ],
    )
    def update_total_hours(_, flow_spread_data):
        df = pd.DataFrame(flow_spread_data)
        total = df["operated_hours"].sum()
        return str(total)

    # normalize hours
    @callback(
        Output(ids.FLOW_SPREAD_TABLE, "rowData"),
        [
            Input(normalize_button.id, "n_clicks"),
            Input(flow_spread_dropdown.id, "value"),
        ],
        [State(ids.FLOW_SPREAD_TABLE, "rowData"), State(flow_spread_total.value_id, "children")],
        prevent_initial_call=True,
    )
    def update_data(n_clicks, dropdown_value, flow_spread_data, total_hours):
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        if ctx.triggered_id == normalize_button.id:
            if n_clicks:
                df = pd.DataFrame(flow_spread_data)
                df["operated_hours"] = (
                    df["operated_hours"]
                    / df["operated_hours"].sum()
                    * float(total_hours)
                )
                return df.to_dict("records")

        elif ctx.triggered_id == flow_spread_dropdown.id:
            if dropdown_value == "constant":
                df = pd.DataFrame(flow_spread_data)
                df["operated_hours"] = 24 / len(df)
                return df.to_dict("records")
            if dropdown_value == "variable":
                data = {
                    "rated_flow_percentage": [
                        "30%",
                        "40%",
                        "50%",
                        "60%",
                        "70%",
                        "80%",
                        "90%",
                        "100%",
                    ],
                    "operated_hours": [0, 2, 5, 7, 5, 3, 2, 0],
                }
                return pd.DataFrame(data).to_dict("records")
            return dash.no_update
