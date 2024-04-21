import dash
import dash_ag_grid as dag
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from custom_components.input import InputCustom
from rotalysis.pump import Pump

from . import ids

head_input = InputCustom(
    id=ids.PUMP_DESIGN_RATED_HEAD,
    label="Pump Rated Head (m)",
    addon_text="m",
)
rated_flow_input = InputCustom(
    id=ids.PUMP_DESIGN_RATED_FLOW,
    label="Pump Rated Flow (m3/s)",
    addon_text="m3/s",
)
rated_efficiency_input = InputCustom(
    id=ids.PUMP_DESIGN_RATED_EFFICIENCY,
    label="Pump Rated Efficiency (%)",
    addon_text="%",
)
density_input = InputCustom(
    id=ids.PUMP_DENSITY,
    label="Density (kg/m3)",
    addon_text="kg/m3",
)
dialog = dcc.ConfirmDialog(
    id="confirm-input",
    message="callback triggered",
)


def get_pump_curve_grid(flowrates, pump_heads):
    return dag.AgGrid(
        id=ids.PUMP_CURVE_DATA,
        columnDefs=[
            {"headerName": "Flow Rate (m3/h)", "field": "flow_rate", "editable": True},
            {"headerName": "Pump Head (m)", "field": "pump_head", "editable": True},
        ],
        rowData=[
            {"flow_rate": flow, "head": head}
            for flow, head in zip(flowrates, pump_heads)
        ],
    )


def get_system_curve_grid(flowrates, system_heads):
    return dag.AgGrid(
        id=ids.SYSTEM_CURVE_DATA,
        columnDefs=[
            {"headerName": "Flow Rate (m3/h)", "field": "flow_rate", "editable": True},
            {"headerName": "Sytem Head (m)", "field": "system_head", "editable": True},
        ],
        rowData=[
            {"flow_rate": flow, "head": head}
            for flow, head in zip(flowrates, system_heads)
        ],
    )


def get_efficiency_curve_grid(flowrates, efficiencies):
    return dag.AgGrid(
        id=ids.EFFICIENCY_CURVE_DATA,
        columnDefs=[
            {"headerName": "Flow Rate (m3/h)", "field": "flow_rate"},
            {"headerName": "Efficiency (%)", "field": "efficiency"},
        ],
        rowData=[
            {"flow_rate": flow, "efficiency": eff}
            for flow, eff in zip(flowrates, efficiencies)
        ],
    )


sample_fill_button = html.Button(
    id=ids.FILL_SAMPLE_BUTTON,
    children="Fill Sample Data",
    n_clicks=0,
)


def export_container(id: str):
    x, y = list(range(10)), list(range(10))
    return html.Div(
        id=id,
        children=[
            head_input.layout(),
            rated_flow_input.layout(),
            rated_efficiency_input.layout(),
            density_input.layout(),
            sample_fill_button,
            get_pump_curve_grid(x, y),
            get_system_curve_grid(x, y),
            get_efficiency_curve_grid(x, y),
            dialog,
        ],
    )


# Get sample data for pump curve


def register_callbacks():
    @callback(
        Output(ids.PUMP_CURVE_DATA, "rowData"),
        Output(ids.SYSTEM_CURVE_DATA, "rowData"),
        Output(ids.EFFICIENCY_CURVE_DATA, "rowData"),
        Input(ids.FILL_SAMPLE_BUTTON, "n_clicks"),
        State(ids.PUMP_DESIGN_RATED_HEAD, "value"),
        State(ids.PUMP_DESIGN_RATED_FLOW, "value"),
        State(ids.PUMP_DENSITY, "value"),
    )
    def fill_sample_data(n_clicks, rated_head, rated_flow, density):
        if n_clicks == 0:
            raise PreventUpdate

        pump = Pump(rated_head=rated_head, rated_flow=rated_flow, density=density)
        pump_curve = pump.sample_pump_curve[["flow_rate", "pump_head"]]
        system_curve = pump.sample_pump_curve[["flow_rate", "system_head"]]
        efficiency_curve = pump.sample_pump_curve[["flow_rate", "efficiency"]]

        return (
            pump_curve.to_dict(orient="records"),
            system_curve.to_dict(orient="records"),
            efficiency_curve.to_dict(orient="records"),
        )
