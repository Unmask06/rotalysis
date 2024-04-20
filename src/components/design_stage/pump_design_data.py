import dash_ag_grid as dag
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from custom_components.input import InputCustom
import pandas as pd

from . import ids

pump_curve_data = 

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
pump_curve_data = dag.AgGrid(
    id=ids.PUMP_CURVE_DATA,
    columnDefs=[
        {"headerName": "Flow Rate (m3/h)", "field": "flow_rate"},
        {"headerName": "Head (m)", "field": "head"},
    ],
    rowData=[{"flow_rate": 0, "head": 0}],
)


def export_container(id: str):
    return html.Div(
        id=id,
        children=[
            head_input.layout(),
            rated_flow_input.layout(),
            rated_efficiency_input.layout(),
            density_input.layout(),
            pump_curve_data,
            dialog,
        ],
    )


def register_callbacks():
    pass
