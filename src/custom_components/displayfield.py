from dash import html
from dataclasses import dataclass


@dataclass
class DisplayField:
    """ Custom display field component using Dash HTML components."""
    label: str = "Label"
    value: str = ""
    addon_text: str = ""

    @property
    def layout(self):
        """
        Generates the HTML layout for the display field component.
        :return: A Dash HTML Div element containing the component layout.
        """
        return html.Div(
            className="flex items-center space-x-2 m-4",
            children=[
                html.Span(
                    self.label,
                    className="text-sm font-medium text-gray-900",
                ),
                html.Span(
                    f": {self.value}",
                    className="text-sm text-gray-700",
                ),
                html.Span(
                    self.addon_text,
                    className="text-sm text-gray-500" if self.addon_text else "hidden",
                ),
            ],
        )
