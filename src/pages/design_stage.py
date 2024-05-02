"""This module compiles the layout and callbacks of the design stage page."""

import dash
from dash import html

from components.design_stage import energy_savings_data as esdc
from components.design_stage import pump_design_data as pddc
from components.design_stage import pump_operation_data as podc

dash.register_page(__name__)

pump_design_input = pddc.export_container()
pump_operation_input = podc.export_container()
energy_savings = esdc.export_container()


layout = html.Div(
    [
        html.H1("Pump Design Stage Energy Calculation", className="text-2xl font-bold p-4"),
        pump_design_input,
        pump_operation_input,
        energy_savings,
    ], className="container mx-auto p-4",
)

pddc.register_callbacks()
podc.register_callbacks()
esdc.register_callbacks()
