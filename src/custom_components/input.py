from dash import html, dcc


class InputCustom:
    def __init__(
        self,
        id="input-1",
        label="Label",
        type="text",
        value="",
        addon_text="",
        help_text="",
        error_message="",
    ):
        """
        Initialize the input form component with label, default value, help text, addon text, and an initial error message.
        :param label: Text for the label associated with the input field.
        :param value: Default value for the input field.
        :param id_prefix: A prefix for the component's IDs to ensure uniqueness.
        :param help_text: Help text displayed below the input field.
        :param addon_text: Text for the trailing add-on.
        :param error_message: Initial error message to display.
        """
        self.label = label
        self.type = type
        self.value = value
        self.id = id
        self.help_text = help_text
        self.addon_text = addon_text
        self.error_message = error_message  # Initialize with an error message

    def layout(self):
        """
        Generates the HTML layout for the input form component.
        :return: A Dash HTML Div element containing the component layout.
        """
        return html.Div(
            [
                html.Label(
                    self.label,
                    className="block text-sm font-medium text-gray-900",
                    htmlFor=f"{self.id}",
                ),
                html.Div(
                    className="mt-1 flex rounded-md shadow-sm",
                    children=[
                        dcc.Input(
                            type=self.type,
                            value=self.value,
                            id=f"{self.id}",
                            className="block w-full rounded-none rounded-l-md shadow-sm border-0 border-gray-500 px-2 py-1.5 text-gray-900  ring-1 ring-inset ring-gray-400 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
                            placeholder="Enter value",
                        ),
                        html.Span(
                            self.addon_text,
                            className="inline-flex items-center shadow-sm rounded-r-md border border-l-0 border-gray-500 px-2 py-1.5 text-gray-900 sm:text-sm",
                        ),
                    ],
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
