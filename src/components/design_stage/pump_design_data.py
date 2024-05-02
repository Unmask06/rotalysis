"""Pump design data container."""

import dash
import pandas as pd
from agility.skeleton.custom_components import (
    ButtonCustom,
    ContainerCustom,
    DropdownCustom,
    InputCustom,
)
from dash import callback, callback_context, html
from dash.dependencies import Input, Output, State
from dash_ag_grid import AgGrid

import rotalysis.pump.curve_generator as cg
from rotalysis.pump import Pump
from rotalysis.pump import PumpFunction as PF

from . import ids

calc_level_dropdown = DropdownCustom(
    options=[
        {"label": "Rated Head and Flow", "value": "two_points"},
        {"label": "Rated Head, Flow and Shutoff Head", "value": "three_points"},
        {"label": "Multiple Points", "value": "multiple_points"},
    ],
    label="Calculation Level",
    help_text="Select the level of calculation for the pump curve based on the data availability.",
)

# Input Fields ---------------------------------------------------------------
head_input = InputCustom(
    label="Pump Rated Head",
    addon_text="m",
)
rated_flow_input = InputCustom(
    label="Pump Rated Flow",
    addon_text="m3/h",
)
rated_efficiency_input = InputCustom(
    label="Pump Rated Efficiency",
    addon_text="%",
)
density_input = InputCustom(
    label="Density",
    addon_text="kg/m3",
)

shutoff_head_input = InputCustom(
    label="Shutoff Head",
    addon_text="m",
)
static_head_input = InputCustom(
    label="Static Head",
    addon_text="m",
)

# Grids ---------------------------------------------------------------------
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
    defaultColDef={"resizable": True, "editable": True, "width": "150"},
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

# Buttons -------------------------------------------------------------------
sample_fill_button = ButtonCustom(label="Populate typical pump curve data")
generate_data_points_button = ButtonCustom(
    label="Generate Data Points", button_props={"style": {"display": "none"}}
)


# Containers Creation ----------------------------------------------------------
input_container = ContainerCustom(
    [
        head_input.layout,
        rated_flow_input.layout,
        rated_efficiency_input.layout,
        density_input.layout,
        shutoff_head_input.layout,
        static_head_input.layout,
        generate_data_points_button.layout,
    ],
    html_props={"style": {"display": "none"}},
)

curve_grid_container = ContainerCustom(
    [
        sample_fill_button.layout,
        html.Div([pump_curve_grid], className="flex-1 p-2 border"),
        html.Div([system_curve_grid], className="flex-1 p-2 border"),
        html.Div([efficiency_curve_grid], className="flex-1 p-2 border"),
    ],
    classname="flex flex-row",
    html_props={"style": {"display": "none"}},
)


def export_container():
    return ContainerCustom(
        [
            calc_level_dropdown.layout,
            input_container.layout,
            curve_grid_container.layout,
        ],
    ).layout


# Get sample data for pump curve


def register_callbacks():

    @callback(
        [
            Output(input_container.id, "style"),
            Output(curve_grid_container.id, "style"),
            Output(generate_data_points_button.id, "style"),
            Output(pump_curve_grid.id, "rowData"),
            Output(system_curve_grid.id, "rowData"),
            Output(efficiency_curve_grid.id, "rowData"),
        ],
        [
            Input(calc_level_dropdown.id, "value"),
            Input(sample_fill_button.id, "n_clicks"),
            Input(generate_data_points_button.id, "n_clicks"),
        ],
        [
            State(head_input.id, "value"),
            State(rated_flow_input.id, "value"),
            State(density_input.id, "value"),
            State(rated_efficiency_input.id, "value"),
            State(shutoff_head_input.id, "value"),
            State(static_head_input.id, "value"),
        ],
        prevent_initial_call=True,
    )
    def update_output(
        calc_level,
        sample_clicks,
        generate_clicks,
        rated_head,
        rated_flow,
        density,
        rated_efficiency,
        shutoff_head,
        static_head,
    ):
        ctx = callback_context

        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        if calc_level in ["two_points", "three_points"]:
            input_style = {"display": "block"}
            grid_style = {"display": "block"}
            button_style = {"display": "block"}
        else:
            input_style = {"display": "block"}
            grid_style = {"display": "block"}
            button_style = {"display": "none"}

        if ctx.triggered_id == calc_level_dropdown.id:

            # Handling different calculation levels

            return (
                input_style,
                grid_style,
                button_style,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        # Sample data fill
        if ctx.triggered_id == sample_fill_button.id:
            pump = Pump(
                rated_head=float(rated_head),
                rated_flow=float(rated_flow),
                density=float(density),
            )
            pump_curve = (
                pump.sample_pump_curve[["flow_rate", "pump_head"]]
                .round(2)
                .to_dict(orient="records")
            )
            system_curve = (
                pump.sample_pump_curve[["flow_rate", "system_head"]]
                .round(2)
                .to_dict(orient="records")
            )
            efficiency_curve = (
                pump.sample_pump_curve[["flow_rate", "efficiency"]]
                .round(2)
                .to_dict(orient="records")
            )
            return (
                input_style,
                grid_style,
                button_style,
                pump_curve,
                system_curve,
                efficiency_curve,
            )

        # Generate data points based on input
        if ctx.triggered_id == generate_data_points_button.id:
            # Flow Curve
            if calc_level == "two_points":
                a, b, c = cg.get_headcurve_coeff_from_twopoint(
                    float(rated_flow), float(rated_head)
                )
            if calc_level == "three_points":
                a = cg.solve_coefficient(
                    float(rated_flow),
                    float(rated_head),
                    1,
                    b=0,
                    noflow_head=float(shutoff_head),
                )
                b, c = 0, float(shutoff_head)

            flow_rates = [float(rated_flow) * i / 10 for i in range(11)]
            heads = [
                cg.get_head_from_curve(flow_rate, a, b, c) for flow_rate in flow_rates
            ]
            pump_curve = (
                pd.DataFrame({"flow_rate": flow_rates, "pump_head": heads})
                .round(2)
                .to_dict(orient="records")
            )

            # System Curve
            a = cg.solve_coefficient(
                flow=float(rated_flow),
                head=float(rated_head),
                initial_guess=1,
                b=0,
                noflow_head=float(static_head),
            )

            b, c = 0, 0

            system_curve = (
                pd.DataFrame(
                    {
                        "flow_rate": flow_rates,
                        "system_head": [
                            cg.get_head_from_curve(flow_rate, a, b, c)
                            for flow_rate in flow_rates
                        ],
                    }
                )
                .round(2)
                .to_dict(orient="records")
            )

            # Efficiency Curve

            efficiencies = [
                PF.get_pump_efficiency(
                    float(rated_flow), float(rated_efficiency), float(flow)
                )
                * 100
                for flow in flow_rates
            ]
            efficiency_curve = (
                pd.DataFrame({"flow_rate": flow_rates, "efficiency": efficiencies})
                .round(2)
                .to_dict(orient="records")
            )

            return (
                input_style,
                grid_style,
                button_style,
                pump_curve,
                system_curve,
                efficiency_curve,
            )

        raise dash.exceptions.PreventUpdate
