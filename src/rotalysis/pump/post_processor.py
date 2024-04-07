"""
src/rotalysis/pump/post_processor.py
This module responsible for generating the graphs and figures for the pump data.
Also, formatting the data for the pump data.
"""

import pandas as pd
from rotalysis import definitions as defs
import plotly.graph_objects as go
from plotly.subplots import make_subplots


xl_path = r"D:\Code\rotalysis\src\data\output\Output.xlsx" # TODO: Change this path to the correct path
df = pd.read_excel(xl_path, sheet_name=1, index_col=0)
df2 = pd.read_excel(xl_path, sheet_name=2, index_col=0)


df.dropna(subset=[defs.ComputedVariables.FLOWRATE_PERCENT], inplace=True)
df2.dropna(subset=[defs.ComputedVariables.FLOWRATE_PERCENT], inplace=True)


fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Bar(
        x=df[defs.ComputedVariables.FLOWRATE_PERCENT],
        y=df[defs.ComputedVariables.WORKING_PERCENT],
        name="Flowrate %",
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=df2[defs.ComputedVariables.FLOWRATE_PERCENT],
        y=df2[defs.ComputedVariables.ANNUAL_ENERGY_SAVING],
        mode="lines+markers",
        name="Annual Energy Saving (Impeller Trim)",
    ),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(
        x=df[defs.ComputedVariables.FLOWRATE_PERCENT],
        y=df[defs.ComputedVariables.ANNUAL_ENERGY_SAVING],
        mode="lines",
        name="Annual Energy Saving (VSD)",
    ),
    secondary_y=True,
)

fig.update_layout(
    title="Energy Savings upon implementing the VSD and Impeller Trim",
    xaxis_title="% of Rated Flowrate",
    yaxis_title="Working %",
    yaxis2={
        "title": "Annual Energy Saving (MWh)",
        "titlefont": {"color": "blue"},
        "tickfont": {"color": "blue"},
    },
)

