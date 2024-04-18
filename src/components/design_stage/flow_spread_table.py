import dash
import pandas as pd
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html

from . import ids

# Define column headers
percentage_columns = [
    {"name": f"{i}%", "id": f"{i}%", "type": "numeric", "editable": True}
    for i in range(30, 101, 10)
]
columns = percentage_columns + [{"name": "Total", "id": "Total", "editable": False}]

# Initialize a DataFrame
data = pd.DataFrame([{col["id"]: 0 for col in percentage_columns}])
data["Total"] = data.sum(axis=1)


def render():
    # Callback to update the total whenever any cell value changes
    return html.Div(
        [
            dash_table.DataTable(
                id="percentage-table",
                columns=columns,
                data=data.to_dict("records"),
                editable=True,
                style_cell={"textAlign": "center"},
            ),
            html.Button("Normalize", id=ids.NORMAL_HOURS_BUTTON),
        ]
    )
