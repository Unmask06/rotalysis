from dataclasses import dataclass

from dash import html


@dataclass
class Button:
    """Custom checkbox component using Dash HTML components html.Button."""

    id: str
    label: str
    color: str = "bg-blue-500"
    hidden: bool = False

    def __post_init__(self):
        if self.hidden:
            self.style = {"display": "none"}
        else:
            self.style = {}

    @property
    def layout(self) -> html.Button:
        """
        Generates the HTML layout for the button component.

        :return: A Dash HTML component representing the button.
        """
        return html.Button(
            self.label,
            id=self.id,
            className=f"{self.color} hover:bg-blue-700 text-white py-2 px-4 m-2 w-40",
            style=self.style,
        )
