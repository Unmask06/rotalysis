from pathlib import Path

from pydantic import BaseModel, field_validator


class RotalysisInput(BaseModel):
    INPUT_FOLDER: str
    OUTPUT_FOLDER: str
    CONFIG_FILE: str
    TASKLIST_FILE: str

    @field_validator("INPUT_FOLDER")
    def input_folder_validator(cls, v):
        if not Path(v).is_dir():
            raise ValueError(f"{v} is not a valid directory")
        return v

    @field_validator("OUTPUT_FOLDER")
    def output_folder_validator(cls, v):
        if not Path(v).is_dir():
            raise ValueError(f"{v} is not a valid directory")
        return v

    @field_validator("CONFIG_FILE")
    def config_file_validator(cls, v):
        if not Path(v).is_file():
            raise ValueError(f"{v} is not a valid file")
        return v

    @field_validator("TASKLIST_FILE")
    def tasklist_file_validator(cls, v):
        if not Path(v).is_file():
            raise ValueError(f"{v} is not a valid file")
        return v
