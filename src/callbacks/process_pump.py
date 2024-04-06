import base64
import io
from typing import Dict, Tuple

import pandas as pd
from dash import Dash, html
from dash.dependencies import Input, Output, State

from components import ids
from rotalysis.definitions import InputSheetNames
from rotalysis.pump import Pump

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
        else:
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
        Output(ids.OUTPUT_PROCESS_PUMP, "children"),
        Input(ids.BUTTON_PROCESS_PUMP, "n_clicks"),
        State(ids.STORE_DATA, "data"),
        prevent_initial_call=True,
    )
    def process_pump(n_clicks: int, data: Dict[str, str]) -> html.Div:
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

        return html.Div(
            [
                html.H5("Pump has been processed."),
                html.Button("Download the result", id=ids.DOWNLOAD_BUTTON),
            ]
        )
