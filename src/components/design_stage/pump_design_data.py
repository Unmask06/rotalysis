"""Pump design data container."""

import pandas as pd
from agility.skeleton.custom_components import (
    AgGridCustom,
    ButtonCustom,
    ContainerCustom,
    InputCustom,
)
from dash import callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

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

pump_curve_grid = AgGridCustom(
    df=pd.DataFrame(
        data={
            "flow_rate": ["" for i in range(10)],
            "pump_head": ["" for i in range(10)],
        }
    ),
    editable=True,
    ag_grid_props={"className": "flex-auto p-4 border"},
)
system_curve_grid = AgGridCustom(
    df=pd.DataFrame(
        data={
            "flow_rate": ["" for i in range(10)],
            "system_head": ["" for i in range(10)],
        }
    ),
    editable=True,
    ag_grid_props={"className": "flex-auto p-4 border"},
)
efficiency_curve_grid = AgGridCustom(
    df=pd.DataFrame(
        data={
            "flow_rate": ["" for i in range(10)],
            "efficiency": ["" for i in range(10)],
        }
    ),
    editable=True,
    ag_grid_props={"className": "flex-auto p-4 border"},
)

curve_grid_container = ContainerCustom(
    [
        pump_curve_grid.layout,
        system_curve_grid.layout,
        efficiency_curve_grid.layout,
    ],
)


def export_container():
    return ContainerCustom(
        [
            head_input.layout,
            rated_flow_input.layout,
            rated_efficiency_input.layout,
            density_input.layout,
            sample_fill_button.layout,
            pump_curve_grid.layout,
            system_curve_grid.layout,
            efficiency_curve_grid.layout,
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
        pump_curve = pump.sample_pump_curve[["flow_rate", "pump_head"]]
        system_curve = pump.sample_pump_curve[["flow_rate", "system_head"]]
        efficiency_curve = pump.sample_pump_curve[["flow_rate", "efficiency"]]

        return (
            pump_curve.to_dict(orient="records"),
            system_curve.to_dict(orient="records"),
            efficiency_curve.to_dict(orient="records"),
        )
