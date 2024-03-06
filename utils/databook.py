# databook.py
# This file need DataBook.xlsx file to be present in the input folder.

from pathlib import Path

import pandas as pd
import xlwings as xw


class Databook:
    def __init__(self, databook_path: str = "utils/Databook.xlsx"):
        self.databook_path = databook_path
        self.databook_path = Path(self.databook_path).resolve()

        if not Path(self.databook_path).is_file():
            raise FileNotFoundError(f"{self.databook_path} not found")

        self.databook: xw.Book = xw.Book(databook_path)

    def get_dataframe(
        self, sheet_name: str, cell_range: str, first_col_as_index: bool = False
    ):
        if sheet_name not in [sheet.name for sheet in self.databook.sheets]:
            raise ValueError(f"{sheet_name} not found in the databook")

        sheet = self.databook.sheets[sheet_name]
        range_end = (
            sheet.range(cell_range)
            .expand()
            .end("down")
            .end("right")
            .get_address(False, False)
        )

        df = (
            sheet.range(f"{cell_range}:{range_end}")
            .options(pd.DataFrame, header=1, index=first_col_as_index)
            .value
        )
        return df
