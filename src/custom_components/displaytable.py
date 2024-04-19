from dash import html, dash_table
import pandas as pd


class DisplayTable:
    def __init__(self, dataframe: pd.DataFrame, table_id: str):
        """
        Initialize the custom Dash DataTable component.

        :param dataframe: Pandas DataFrame to display.
        :param table_id: HTML id attribute for the DataTable.
        """
        self.dataframe = dataframe
        self.table_id = table_id

    def layout(self):
        """
        Render the DataTable as an HTML Div containing the styled DataTable.

        :return: A Dash html.Div object containing the DataTable.
        """
        return html.Div(
            [
                dash_table.DataTable(
                    id=self.table_id,
                    columns=[{"name": i, "id": i} for i in self.dataframe.columns],
                    data=self.dataframe.to_dict("records"),
                    style_cell={"textAlign": "center"},
                    style_header={
                        "backgroundColor": "WhiteSmoke",
                        "fontWeight": "bold",
                        "color": "black",
                        "border": "1px solid lightgray",
                    },
                    style_data_conditional=[
                        {
                            "if": {"column_id": self.dataframe.columns[0]},
                            "backgroundColor": "WhiteSmoke",
                            "color": "black",
                            "border": "1px solid lightgray",
                        }
                    ],
                )
            ]
        )
