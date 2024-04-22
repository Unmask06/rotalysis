"""This module compiles the layout and callbacks of the design stage page."""

import dash
from dash import html

from components.design_stage import energy_savings_data as esdc
from components.design_stage import ids
from components.design_stage import pump_design_data as pddc
from components.design_stage import pump_operation_data as podc

dash.register_page(__name__)

pump_design_input = pddc.export_container(ids.PUMP_DESIGN_INPUT_CONTAINER)
pump_operation_input = podc.export_container(ids.PUMP_OPERATION_INPUT_CONTAINER)
energy_savings = esdc.export_container(ids.ENERGY_SAVINGS_CONTAINER)


layout = html.Div(
    [
        html.H1("Design Stage"),
        pump_design_input,
        pump_operation_input,
        energy_savings,
    ]
)

pddc.register_callbacks()
podc.register_callbacks()
esdc.register_callbacks()
