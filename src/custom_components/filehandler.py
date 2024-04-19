import dash
from dash import html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import json
import base64

# Assuming 'Project' and 'InfoSchema' are defined elsewhere as before
from project import Project as PRJ
from components.calculation.button import Button
from components.message import Message

store_id = "global-store"


class FileHandler:
    def __init__(self, id_suffix, store_id):
        self.id_suffix = id_suffix
        self.store_id = store_id
        self.setup_callbacks()

    def layout(self):
        return html.Div(
            [
                html.Div(
                    [
                        Button(
                            self._id("btn-new"), "New", "bg-blue-500", hidden=False
                        ).layout(),
                        dcc.Upload(
                            Button(
                                "btn-open", "Open", "bg-purple-500", hidden=False
                            ).layout(),
                            id=self._id("btn-open"),
                            multiple=False,
                        ),
                        Button(
                            self._id("btn-save"), "Save", "bg-green-500", hidden=True
                        ).layout(),
                        Button(
                            self._id("btn-close"), "Close", "bg-red-500", hidden=True
                        ).layout(),
                        dcc.Download(id=self._id("download")),
                    ],
                    className="flex",
                ),
                html.Div(id=self._id("feedback"), className="mt-4"),
            ]
        )

    def _id(self, name):
        return f"fh-{name}-{self.id_suffix}"

    def setup_callbacks(self):

        # callback function to show buttons based on project open or close status.
        # If project is open then show save and close button, otherwise show new and open button
        @callback(
            Output(self._id("btn-new"), "style"),
            Output(self._id("btn-open"), "style"),
            Output(self._id("btn-save"), "style"),
            Output(self._id("btn-close"), "style"),
            [Input(self.store_id, "data"), Input("url", "pathname")],
        )
        def show_buttons(data, pathname):
            if data is not None:
                # If data is loaded, hide 'New' and 'Open' buttons, show 'Save' and 'Close' buttons
                return {"display": "none"}, {"display": "none"}, {}, {}
            else:
                # If no data is loaded, show 'New' and 'Open' buttons, hide 'Save' and 'Close' buttons
                return {}, {}, {"display": "none"}, {"display": "none"}

        @callback(
            [
                Output(self.store_id, "data"),
                Output(self._id("download"), "data"),
                Output(self._id("feedback"), "children"),
            ],
            [
                Input(self._id("btn-new"), "n_clicks"),
                Input(self._id("btn-open"), "contents"),
                Input(self._id("btn-save"), "n_clicks"),
                Input(self._id("btn-close"), "n_clicks"),
            ],
            [State(self.store_id, "data")],
            prevent_initial_call=True,
        )
        def handle_file_actions(new, contents, save, close, data):
            ctx = dash.callback_context
            if not ctx.triggered or ctx.triggered[0]["value"] is None:
                raise PreventUpdate

            data = data or {}  # Ensure data is always a dictionary
            download_data = dash.no_update  # Default download data
            feedback_html = None  # Default feedback, to be set based on actions

            try:
                action_type = ctx.triggered[0]["prop_id"].split(".")[0].split("-")[2]
                if action_type == "new":
                    with open("project_default.json", "r") as f:
                        project_data = json.load(f)
                        project_data, is_valid, error_messages = (
                            PRJ.validate_project_data(project_data)
                        )
                        if is_valid:
                            data = project_data
                            feedback_html = Message(
                                messages="New project loaded sucessfully",
                                success=True,
                            ).layout()

                        else:
                            feedback_html = Message(
                                messages=error_messages,
                                heading="Failure",
                                success=False,
                            ).layout()

                elif action_type == "open" and contents:
                    content_type, content_string = contents.split(",")
                    decoded = base64.b64decode(content_string)
                    project_data = json.loads(decoded.decode("utf-8"))
                    project_data, is_valid, error_messages = PRJ.validate_project_data(
                        project_data
                    )
                    if is_valid:
                        data = project_data
                        feedback_html = Message(
                            messages="Project opened successfully",
                            success=True,
                        ).layout()

                    else:
                        feedback_html = Message(
                            messages=error_messages,
                            heading="Failure",
                            success=False,
                        ).layout()

                elif action_type == "save":
                    project_data, is_valid, error_messages = PRJ.validate_project_data(
                        data
                    )
                    if is_valid:
                        download_data = dict(
                            content=json.dumps(project_data, indent=4),
                            filename="project_data.json",
                        )
                        feedback_html = Message(
                            "Project saved successfully", success=True
                        ).layout()
                    else:
                        feedback_html = Message(
                            messages="No project to save",
                            success=False,
                        ).layout()

                elif action_type == "close":
                    project_data, is_valid, error_messages = PRJ.validate_project_data(
                        data
                    )
                    if is_valid:
                        data = None
                        feedback_html = Message(
                            messages="Project closed", success=True
                        ).layout()
                    else:
                        feedback_html = html.Span(
                            "No project was open to close.", className="text-red-500"
                        )

            except Exception as e:
                feedback_html = html.Span(f"Error: {e}", className="text-red-500")

            return data, download_data, feedback_html
