""" inputs.py"""

from pathlib import Path

from pydantic import BaseModel, field_validator


class RotalysisInput(BaseModel):
    """Pydantic model for input parameters required by the Rotalysis application."""

    INPUT_FOLDER: str
    OUTPUT_FOLDER: str
    CONFIG_FILE: str
    TASKLIST_FILE: str

    @field_validator("INPUT_FOLDER")
    @classmethod
    def input_folder_validator(cls, v):
        if not Path(v).is_dir():
            raise ValueError(f"{v} is not a valid directory")
        return v

    @field_validator("OUTPUT_FOLDER")
    @classmethod
    def output_folder_validator(cls, v):
        if not Path(v).is_dir():
            raise ValueError(f"{v} is not a valid directory")
        return v

    @field_validator("CONFIG_FILE")
    @classmethod
    def config_file_validator(cls, v):
        if not Path(v).is_file():
            raise ValueError(f"{v} is not a valid file")
        return v

    @field_validator("TASKLIST_FILE")
    @classmethod
    def tasklist_file_validator(cls, v):
        if not Path(v).is_file():
            raise ValueError(f"{v} is not a valid file")
        return v
