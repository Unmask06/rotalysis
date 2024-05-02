"""
pages/calculation.py - Calculation page for the Rotalysis app.
"""

import dash
from agility.skeleton.custom_components import ContainerCustom
from dash import dcc, html

from components.calculation import calculation, ids

dash.register_page(__name__)


layout = ContainerCustom(
    [
        html.H1("Calculation Page", className="text-center text-2xl font-bold"),
        calculation.export_container(),
    ]
).layout

calculation.register_callbacks()
