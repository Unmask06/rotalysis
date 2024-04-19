from dash import html


class Message:
    def __init__(self, messages=None, heading=None, success=True):
        """
        Initialize the component with messages, an optional heading, and type (success or error).
        :param messages: A string or list of strings, each representing a message.
        :param heading: An optional string for the heading of the message box. If None, no heading is displayed.
        :param success: A boolean flag indicating if the messages are for success (True) or error (False).
        """
        self.messages = [messages] if isinstance(messages, str) else messages
        self.heading = heading
        self.success = success

    def layout(self):
        """
        Generate the Dash component layout for the messages.
        :return: A Dash HTML component representing the message box.
        """
        if not self.messages:
            return html.Div()  # Return an empty Div if there are no messages

        # Set colors and icons based on success or error
        bg_color = "bg-green-50" if self.success else "bg-red-50"
        text_color = "text-green-800" if self.success else "text-red-800"
        list_color = "text-green-700" if self.success else "text-red-700"
        icon_class = "fas fa-check-circle" if self.success else "fas fa-times-circle"

        icon_element = html.I(
            className=f"{icon_class} {text_color} fa-lg", style={"marginRight": "8px"}
        )

        heading_element = (
            html.H3(
                className=f"text-sm font-medium {text_color}", children=self.heading
            )
            if self.heading
            else None
        )

        # Render messages directly or as a list, based on the count
        if len(self.messages) == 1:
            message_content = html.Div(
                className=f"{list_color}", children=self.messages[0]
            )
        else:
            message_content = html.Ul(
                role="list",
                className=f"list-disc space-y-1 pl-5 {list_color}",
                children=[html.Li(message) for message in self.messages],
            )

        return html.Div(
            className=f"rounded-md {bg_color} p-4",
            children=[
                html.Div(
                    className="flex",
                    children=[
                        html.Div(className="flex-shrink-0", children=[icon_element]),
                        html.Div(
                            className="ml-3",
                            children=(
                                [heading_element, message_content]
                                if heading_element
                                else [message_content]
                            ),
                        ),
                    ],
                ),
            ],
        )
