from dash import html, dcc


class CheckboxCustom:
    def __init__(
        self,
        id="checkbox-1",
        options=[],
        value=[],
        label="Label",
        help_text="",
        error_message="",
    ):
        self.label = label
        self.options = options
        self.value = value
        self.id = id
        self.help_text = help_text
        self.error_message = error_message

    def layout(self):

        return html.Div(
            [
                dcc.Checklist(
                    id=self.id,
                    options=self.options,
                    value=self.value,
                    className="block w-full rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 sm:text-sm",
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
