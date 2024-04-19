from dash import callback, html
from dash.dependencies import Input, Output


class Button:
    def __init__(self, id, label, color="bg-blue-500", hidden=False):
        """
        Initialize the reusable button component.

        :param id_prefix: A unique identifier prefix for the button to ensure component uniqueness.
        :param label: The label text to display on the button.
        :param button_style: A string representing additional CSS classes for styling the button.
        :param output_element_id: The ID of an element where the button's action output will be displayed.
        """
        self.id = id
        self.label = label
        self.color = color
        self.hidden = hidden

    def render(self):
        """
        Generate the layout for the button component.

        :return: A Dash HTML component representing the button.
        """

        if self.hidden:
            style = {"display": "none"}
        else:
            style = {}

        return html.Button(
            self.label,
            id=f"{self.id}",
            className=f"{self.color} hover:bg-blue-700 text-white py-2 px-4 m-2 w-40",
            style=style,
        )
