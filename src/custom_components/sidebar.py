from dash import html, dcc, Input, Output, callback
from project import Project as PRJ

# Assuming CONFIG_PAGE and store_id are defined appropriately
from configurations import CONFIG_PAGE

STORE_ID = "global-store"


class Sidebar:
    def __init__(self, config, store_id):
        self.config = config
        self.store_id = store_id

    def create_nav_item(self, item, progress):
        icon_class, icon_color = self.determine_icon(progress)
        return html.Div(
            className="flex items-center gap-2",
            children=[
                html.I(className=f"{icon_class} {icon_color} text-lg"),
                html.A(
                    item.get("name", ""),
                    href=item.get("path", "#"),
                    className="text-gray-700 hover:text-blue-500 py-2 px-4 rounded-md text-sm font-medium",
                    style={"lineHeight": "1.5"},
                ),
            ],
        )

    def generate_sidebar_content(self, progress):
        # Generate the sidebar content based on progress
        return html.Div(
            children=[
                html.Div(
                    className="p-4",
                    children=[
                        html.H2(
                            self.config["sidenav_title"],
                            className="font-semibold text-xl mt-4 mb-2",
                        ),
                    ],
                ),
                html.Div(
                    className="flex flex-col",
                    children=[
                        self.create_nav_item(item, progress.get(item["name"], 0))
                        for item in self.config["nav_items"]
                    ],
                ),
            ],
            className=" overflow-y-auto p-4",
        )

    def determine_icon(self, progress):
        if progress == 0:
            return "far fa-circle", "text-gray-500"
        if progress == 1:
            return "fas fa-adjust", "text-yellow-500"
        if progress == 2:
            return "fas fa-check-circle", "text-green-500"

    def layout(self):
        # This method now returns the sidebar container with a specific ID
        # The initial content is generated based on default or initial progress
        initial_progress = {item["name"]: 0 for item in self.config["nav_items"]}
        sidebar_content = self.generate_sidebar_content(initial_progress)

        return html.Div(
            id="sidebar-content",  # This ID is used for the callback output
            children=[sidebar_content],
            className=" overflow-y-auto p-4",
        )


# Define the callback to update the sidebar based on `dcc.Store` data
@callback(
    Output("sidebar-content", "children"),
    [Input(STORE_ID, "data"), Input("url", "pathname")],
)
def update_sidebar(data, pathname):
    progress = PRJ.get_progress(data)  # Get progress from your Project class
    sidebar_instance = Sidebar(CONFIG_PAGE, store_id=STORE_ID)
    return sidebar_instance.generate_sidebar_content(progress)
