"""Pump design data container."""

import pandas as pd
from agility.skeleton.custom_components import (
    AgGridCustom,
    ButtonCustom,
    ContainerCustom,
    InputCustom,
)
from dash import callback, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid

from rotalysis.pump import Pump

from . import ids

head_input = InputCustom(
    label="Pump Rated Head",
    addon_text="m",
)
rated_flow_input = InputCustom(
    label="Pump Rated Flow",
    addon_text="m3/s",
)
rated_efficiency_input = InputCustom(
    label="Pump Rated Efficiency",
    addon_text="%",
)
density_input = InputCustom(
    label="Density",
    addon_text="kg/m3",
)

sample_fill_button = ButtonCustom(label="Populate typical pump curve data")

pump_curve_grid = AgGrid(
    id=ids.PUMP_CURVE_GRID,
    columnDefs=[
        {
            "headerName": "Flow Rate",
            "field": "flow_rate",
            "editable": True,
        },
        {
            "headerName": "Pump Head",
            "field": "pump_head",
            "editable": True,
        },
    ],
    defaultColDef={"resizable": True, "editable": True,"width":"150"},
    rowData=[{} for _ in range(10)],  # Add 10 blank rows
    className="ag-theme-alpine",
    style={"width": "100%"},
)


system_curve_grid = AgGrid(
    id="system_curve_grid",
    columnDefs=[
        {"headerName": "Flow Rate", "field": "flow_rate", "editable": True},
        {"headerName": "System Head", "field": "system_head", "editable": True},
    ],
    defaultColDef={"resizable": True, "editable": True, "width": "150"},
    rowData=[{} for _ in range(10)],
    className="ag-theme-alpine",
    style={"width": "100%"},
)

# Define the efficiency curve grid
efficiency_curve_grid = AgGrid(
    id="efficiency_curve_grid",
    columnDefs=[
        {"headerName": "Flow Rate", "field": "flow_rate", "editable": True},
        {"headerName": "Efficiency", "field": "efficiency", "editable": True},
    ],
    defaultColDef={"resizable": True, "editable": True, "width": "150"},
    rowData=[{} for _ in range(10)],
    className="ag-theme-alpine",
    style={"width": "100%"},
)

# Create a flex container for the grids
curve_grid_container = html.Div(
    [
        html.Div([pump_curve_grid], className="flex-1 p-2 border"),
        html.Div([system_curve_grid], className="flex-1 p-2 border"),
        html.Div([efficiency_curve_grid], className="flex-1 p-2 border"),
    ],
    className="flex flex-row",
)


def export_container():
    return ContainerCustom(
        [
            head_input.layout,
            rated_flow_input.layout,
            rated_efficiency_input.layout,
            density_input.layout,
            sample_fill_button.layout,
            curve_grid_container,
        ],
    ).layout


# Get sample data for pump curve


def register_callbacks():
    @callback(
        Output(pump_curve_grid.id, "rowData"),
        Output(system_curve_grid.id, "rowData"),
        Output(efficiency_curve_grid.id, "rowData"),
        Input(sample_fill_button.id, "n_clicks"),
        State(head_input.id, "value"),
        State(rated_flow_input.id, "value"),
        State(density_input.id, "value"),
        prevent_initial_call=True,
    )
    def fill_sample_data(_, rated_head, rated_flow, density):
        pump = Pump(rated_head=rated_head, rated_flow=rated_flow, density=density)
        pump_curve = pump.sample_pump_curve[["flow_rate", "pump_head"]].round(2)
        system_curve = pump.sample_pump_curve[["flow_rate", "system_head"]].round(2)
        efficiency_curve = pump.sample_pump_curve[["flow_rate", "efficiency"]].round(2)

        return (
            pump_curve.to_dict(orient="records"),
            system_curve.to_dict(orient="records"),
            efficiency_curve.to_dict(orient="records"),
        )
