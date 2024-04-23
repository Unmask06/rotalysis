import base64
import io
from typing import Dict

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from agility.skeleton.custom_components import ButtonCustom, CustomDataTable
from dash import Input, Output, State, callback, dcc, html, no_update

from components.calculation import ids, upload_file
from rotalysis.definitions import InputSheetNames
from rotalysis.pump import PumpOptimizer, PumpReporter

from . import ids

process_pump_button = ButtonCustom(
    label="Process Pump",
)


def parse_contents(filename: str, contents: str) -> Dict[str, pd.DataFrame] | html.Div:
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "xls" in filename:
            dfs = pd.read_excel(io.BytesIO(decoded), sheet_name=None)
            return dfs
        return html.Div(
            ["The file format is not supported. Please upload a CSV or Excel file."]
        )
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])


def register_callbacks():

    @callback(
        Output(ids.DOWNLOAD_OUTPUT, "data"),
        Input(ids.DOWNLOAD_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def download_result(n_clicks: int):
        if n_clicks is None:
            return None
        return dcc.send_file("src/data/output/Output.xlsx")

    @callback(
        [
            Output(ids.OUTPUT_CONTAINER, "style"),
            Output(ids.OUTPUT_PROCESS_PUMP, "children"),
            Output(ids.OUTPUT_SUMMARY_TABLE, "children"),
            Output(ids.GRAPH_REPORT_ENERGY_SAVINGS, "figure"),
        ],
        [Input(process_pump_button.id, "n_clicks")],
        [State(ids.STORE_DATA, "data")],
        prevent_initial_call=True,
    )
    def process_pump(n_clicks, data):
        config = pd.read_excel("src/data/Config.xlsx", sheet_name="PumpConfig1")
        emission_factor = pd.read_excel(
            "src/data/Config.xlsx", sheet_name="Emission Factor"
        )

        # helper functions

        if n_clicks is None:
            return (
                {"display": "none"},
                "Click the button to process the pump.",
                no_update,
                no_update,
            )
        if not data or "filename" not in data or not data["filename"]:
            return (
                {"display": "block"},
                html.Div("No file has been uploaded."),
                no_update,
                no_update,
            )

        try:
            dfs = parse_contents(data["filename"], data["contents"])
            design_data = dfs[InputSheetNames.DESIGN_DATA]
            operating_data = dfs[InputSheetNames.OPERATIONAL_DATA]
            unit = dfs[InputSheetNames.UNIT]
            pump = PumpOptimizer(
                config=config,
                emission_factor=emission_factor,
                process_data=design_data,
                operation_data=operating_data,
                unit=unit,
            )

            pump.process_pump()
            pump_reporter = PumpReporter(pump)
            pump_reporter.generate_energy_savings_graph()
            df_summary = pump.df_summary.reset_index(drop=False)

            style = {"display": "block"}
            output_msg = html.H5("Pump has been processed.")
            summary_table = CustomDataTable(df=df_summary).layout
            fig = pump_reporter.energy_savings_graph

            return style, output_msg, summary_table, fig

        except Exception as e:
            return (
                {"display": "block"},
                html.Div(f"Error processing pump data: {e}"),
                no_update,
                no_update,
            )
