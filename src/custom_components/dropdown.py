from dataclasses import dataclass, field
from typing import List, Optional

from dash import dcc, html


@dataclass
class DropdownCustom:
    """Custom dropdown component using Dash HTML components dcc.Dropdown."""

    id: str = "dropdown-1"
    label: str = "Label"
    options: List[dict] = field(default_factory=list)
    value: Optional[str] = None
    help_text: str = ""
    error_message: str = ""

    help_text_id: str = field(init=False)
    error_message_id: str = field(init=False)

    def __post_init__(self):
        """
        Validate the options to ensure they are provided and initialize component-specific IDs.
        """
        if not self.options:
            raise ValueError("Options must be provided for the dropdown.")

        self.help_text_id = f"{self.id}-help"
        self.error_message_id = f"{self.id}-error"

    @property
    def layout(self) -> html.Div:
        """
        Generates the HTML layout for the dropdown component.
        """
        component = [
            html.Label(
                self.label,
                htmlFor=self.id,
                className="block text-sm font-medium text-gray-900",
            ),
            dcc.Dropdown(
                id=self.id,
                options=self.options,
                value=self.value,
                className="block w-full rounded-md shadow-sm border border-gray-500 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 sm:text-sm",
            ),
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
        ]
        return html.Div(component, className="m-4")
