from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from custom_components.input import InputCustom

from . import ids

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
dialog = dcc.ConfirmDialog(
    id="confirm-input",
    message="callback triggered",
)


def export_container(id: str):
    return html.Div(
        id=id,
        children=[
            head_input.layout(),
            rated_flow_input.layout(),
            rated_efficiency_input.layout(),
            density_input.layout(),
            dialog,
        ],
    )


def register_callbacks():
    pass
