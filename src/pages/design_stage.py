import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.design_stage import flow_spread_table, ids
from custom_components.dropdown import DropdownCustom
from custom_components.input import InputCustom

dash.register_page(__name__)

head_input = InputCustom(
    id=ids.PUMP_DESIGN_RATED_HEAD,
    label="Pump Rated Head (m)",
    addon_text="m",
)
rated_flow_input = InputCustom(
    id=ids.PUMP_DESIGN_RATED_FLOW,
    label="Pump Rated Flow (m3/hr)",
    addon_text="m3/hr",
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

flow_spread = DropdownCustom(
    id=ids.FLOW_SPREAD,
    label="Flow Spread type",
    options=[
        {"label": "Constant", "value": "constant"},
        {"label": "Variable", "value": "variable"},
    ],
)


# components
pump_design_input = html.Div(
    id=ids.PUMP_DESIGN_INPUT_CONTAINER,
    children=[
        head_input.layout(),
        rated_flow_input.layout(),
        rated_efficiency_input.layout(),
        density_input.layout(),
    ],
)

pump_operation_input = html.Div(
    id=ids.PUMP_OPERATION_INPUT_CONTAINER,
    children=[
        flow_spread.layout(),
    ],
)


def layout():
    return html.Div(
        [
            html.H1("Design Stage"),
            html.Div(pump_design_input),
            html.Div(pump_operation_input),
            flow_spread_table.render(),
        ]
    )
