"""
pages/calculation.py - Calculation page for the Rotalysis app.
"""

import dash
from agility.skeleton.custom_components import ContainerCustom
from dash import dcc, html

from components.calculation import calculation, ids

dash.register_page(__name__)
# def layout():

#     return ContainerCustom(
#         [
#             html.H3("Calculation Page"),
#             calculation.export_container(),
#             html.Button("Process Pump", id=calculation.process_pump_button.id),
#             dcc.Loading(
#                 id=ids.LOADING_PROCESS_PUMP,
#                 type="default",
#                 children=[
#                     html.Div(
#                         id=ids.OUTPUT_PROCESS_PUMP,
#                         children="Process pump to see the result",
#                     )
#                 ],
#             ),
#             ContainerCustom(
#                 [
#                     dcc.Download(id=ids.DOWNLOAD_OUTPUT),
#                     dbc.Button(
#                         id=ids.DOWNLOAD_BUTTON,
#                         children=[
#                             html.I(className="fa-regular fa-circle-down"),
#                             "Download the result",
#                         ],
#                     ),
#                     html.Div(id=ids.OUTPUT_SUMMARY_TABLE),
#                     dcc.Graph(id=ids.GRAPH_REPORT_ENERGY_SAVINGS),
#                 ],
#                 id=ids.OUTPUT_CONTAINER,
#                 style={"display": "none"},
#             ),
#         ]
#     )

layout = ContainerCustom(
    [
        html.H3("Calculation Page"),
        calculation.export_container(),
    ]
).layout

calculation.register_callbacks()
