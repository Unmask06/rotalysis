from dash import html


class DisplayField:
    def __init__(self, label="Label", value="", addon_text=""):
        """
        Initialize the display field component with a label, value, and optional add-on text.
        :param label: The text for the label displayed alongside the value.
        :param value: The value to display.
        :param addon_text: Optional text to display next to the value.
        """
        self.label = label
        self.value = value
        self.addon_text = addon_text

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
