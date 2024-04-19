from dash import html, dcc


class DropdownCustom:
    def __init__(
        self,
        id="dropdown-1",
        label="Label",
        options=[],
        value=None,
        help_text="",
        error_message="",
    ):
        """
        Initialize the dropdown component with label, options, default value, help text, and an initial error message.
        :param label: Text for the label associated with the dropdown.
        :param options: List of dictionaries containing options for the dropdown.
        :param value: Default value for the dropdown.
        :param help_text: Help text displayed below the dropdown.
        :param error_message: Initial error message to display.
        """
        self.label = label
        self.options = options
        self.value = value
        self.id = id
        self.help_text = help_text
        self.error_message = error_message

    def layout(self):
        """
        Generates the HTML layout for the dropdown component.
        :return: A Dash HTML Div element containing the component layout.
        """
        return html.Div(
            [
                html.Label(
                    self.label,
                    className="block text-sm font-medium text-gray-900",
                    htmlFor=f"{self.id}",
                ),
                dcc.Dropdown(
                    id=self.id,
                    options=self.options,
                    value=self.value,
                    className="block w-full rounded-md shadow-sm border border-gray-500  focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 sm:text-sm",
                ),
                html.P(
                    self.help_text,
                    id=f"{self.id}-help",
                    className="mt-2 text-sm text-gray-500",
                ),
                html.Div(
                    self.error_message,
                    id=f"{self.id}-error",
                    className="mt-2 text-sm text-red-600",
                ),
            ],
            className="m-4",
        )
