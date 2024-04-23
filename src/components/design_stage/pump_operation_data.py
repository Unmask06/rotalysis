import dash
import dash_ag_grid as dag
import pandas as pd
from agility.skeleton.custom_components import DropdownCustom
from dash import Dash, callback, dcc, html
from dash.dependencies import Input, Output, State

from . import ids

# Define column headers for AgGrid
percentage_columns = [
    {"field": f"{i}%", "id": f"{i}%", "editable": True, "type": "numericColumn"}
    for i in range(30, 101, 10)
]
columns = percentage_columns + [{"field": "Total", "id": "Total", "editable": False}]

# Initialize a DataFrame
data = pd.DataFrame([{col["id"]: 0 for col in percentage_columns}])
data["Total"] = data.sum(axis=1)

flow_spread_dropdown = DropdownCustom(
    label="Flow Spread Pattern",
    options=[
        {"label": "Constant", "value": "constant"},
        {"label": "Variable", "value": "variable"},
    ],
)

# Using AgGrid instead of a simple Dash DataTable
flow_spread_table = html.Div(
    [
        html.H5("Flow Spread Table"),
        dag.AgGrid(
            id=ids.FLOW_SPREAD_TABLE,
            columnDefs=columns,
            rowData=data.to_dict("records"),
            columnSize="responsiveSizeToFit",
        ),
    ]
)

normalize_button = html.Button("Normalize", id=ids.NORMAL_HOURS_BUTTON)


def export_container(id: str):
    return html.Div(
        [
            flow_spread_dropdown.layout,
            flow_spread_table,
            normalize_button,
        ],
        id=id,
    )


def register_callbacks():

    @callback(
        Output(ids.FLOW_SPREAD_TABLE, "rowData"),
        [
            Input(ids.NORMAL_HOURS_BUTTON, "n_clicks"),
            Input(flow_spread_dropdown.id, "value"),
        ],
        [State(ids.FLOW_SPREAD_TABLE, "rowData")],
        prevent_initial_call=True,
    )
    def update_data(n_clicks, dropdown_value, flow_spread_data):
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == ids.NORMAL_HOURS_BUTTON:
            if n_clicks:
                df = pd.DataFrame(flow_spread_data)
                total = df.sum(axis=1)
                for col in percentage_columns:
                    df[col["id"]] = df[col["id"]] / total * 100
                df["Total"] = df.sum(axis=1)
                return df.to_dict("records")

        elif trigger_id == flow_spread_dropdown.id:
            if dropdown_value == "constant":
                data = pd.DataFrame([{col["id"]: 0 for col in percentage_columns}])
                for col in data.columns:
                    data[col] = 24 / len(data.columns)
                data["Total"] = data.sum(axis=1)
                return data.to_dict("records")
            if dropdown_value == "variable":
                data = pd.DataFrame([{col["id"]: 0 for col in percentage_columns}])
                for i, col in enumerate(data.columns):
                    data[col] = 100 / len(data.columns) * (i + 1)
                data["Total"] = data.sum(axis=1)
                return data.to_dict("records")

        return dash.no_update
