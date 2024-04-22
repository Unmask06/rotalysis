from dataclasses import dataclass, field
from typing import Optional

from dash import dcc, html


@dataclass
class InputCustom:
    """Custom input form component using Dash HTML components dcc.Input."""

    id: str = "input-1"
    label: str = "Label"
    type: str = "text"
    value: Optional[str] = ""
    addon_text: str = ""
    help_text: str = ""
    error_message: str = ""

    help_text_id: str = field(init=False)
    error_message_id: str = field(init=False)

    def __post_init__(self):
        """
        Initialize component-specific IDs for help and error messages.
        """
        self.help_text_id = f"{self.id}-help"
        self.error_message_id = f"{self.id}-error"

    @property
    def layout(self) -> html.Div:
        """
        Generates the HTML layout for the input form component.
        """
        input_group = html.Div(
            className="mt-1 flex rounded-md shadow-sm",
            children=[
                dcc.Input(
                    type=self.type,
                    value=self.value,
                    id=self.id,
                    className="block w-full rounded-none rounded-l-md shadow-sm border-0 border-gray-500 px-2 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-400 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
                    placeholder="Enter value",
                ),
                html.Span(
                    self.addon_text,
                    className="inline-flex items-center shadow-sm rounded-r-md border border-l-0 border-gray-500 px-2 py-1.5 text-gray-900 sm:text-sm",
                ),
            ],
        )

        return html.Div(
            [
                html.Label(
                    self.label,
                    htmlFor=self.id,
                    className="block text-sm font-medium text-gray-900",
                ),
                input_group,
                html.P(
                    self.help_text,
                    id=self.help_text_id,
                    className="mt-2 text-sm text-gray-500",
                ),
                html.Div(
                    self.error_message,
                    id=self.error_message_id,
                    className="mt-2 text-sm text-red-600",
                ),
            ],
            className="m-4",
        )
