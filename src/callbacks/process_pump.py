import base64
import io
from typing import Dict, Tuple

import pandas as pd
from dash import Dash, dash_table, html
from dash.dependencies import Input, Output, State

from components import ids
from rotalysis.definitions import InputSheetNames
from rotalysis.pump import Pump, PumpReporter

config = pd.read_excel("src/data/Config.xlsx", sheet_name="PumpConfig1")
emission_factor = pd.read_excel("src/data/Config.xlsx", sheet_name="Emission Factor")


# helper functions
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


def register_callbacks(app: Dash):
    register_process_pump_callbacks(app)


def register_process_pump_callbacks(app: Dash):

    @app.callback(
        [
            Output(ids.OUTPUT_CONTAINER, "style"),
            Output(ids.OUTPUT_PROCESS_PUMP, "children"),
            Output(ids.OUTPUT_SUMMARY_TABLE, "children"),
            Output(ids.GRAPH_REPORT_ENERGY_SAVINGS, "figure"),
        ],
        Input(ids.BUTTON_PROCESS_PUMP, "n_clicks"),
        State(ids.STORE_DATA, "data"),
        prevent_initial_call=True,
    )
    def process_pump(n_clicks: int, data: Dict[str, str]):
        if n_clicks is None:
            return html.Div("Click the button to process the pump.")
        if not data["filename"]:
            return html.Div("No file has been uploaded.")

        dfs = parse_contents(data["filename"], data["contents"])
        design_data = dfs[InputSheetNames.DESIGN_DATA]
        operating_data = dfs[InputSheetNames.OPERATIONAL_DATA]
        unit = dfs[InputSheetNames.UNIT]
        pump = Pump(
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
        summary_table = dash_table.DataTable(
            data=df_summary.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df_summary.columns],
        )
        fig = pump_reporter.energy_savings_graph

        return (style, output_msg, summary_table, fig)
