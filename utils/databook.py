"""databook.py"""

from pathlib import Path

import pandas as pd
import xlwings as xw


class Databook:
    """
    Class for reading data from an Excel databook using xlwings.
    """

    def __init__(self, databook_path: str = "utils/Databook.xlsx"):
        """
        Initializes the Databook class by setting the path to the databook 
        and verifying its existence.

        :param databook_path: Path to the Excel databook.
        """
        self.databook_path = Path(databook_path).resolve()
        if not self.databook_path.is_file():
            raise FileNotFoundError(f"{self.databook_path} not found")

    def get_dataframe(
        self, sheet_name: str, cell_range: str, first_col_as_index: bool = False
    ) -> pd.DataFrame:
        """
        Retrieves a specified range from a sheet in the databook as a pandas DataFrame.

        :param sheet_name: The name of the sheet to retrieve data from.
        :param cell_range: The cell range (e.g., "A1") to start from.
                            Expands to include the full range automatically.
        :param first_col_as_index: Whether to use the first column as the index of the DataFrame.
        :return: A pandas DataFrame containing the data from the specified sheet and range.
        """
        with xw.App(visible=False):
            book = xw.Book(str(self.databook_path))
            if sheet_name not in [sheet.name for sheet in book.sheets]:
                raise ValueError(f"{sheet_name} not found in the databook")

            sheet = book.sheets[sheet_name]
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
