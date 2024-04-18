"""components/navbar.py"""

from dash import Dash, callback, dcc, html
from dash.dependencies import Input, Output, State


def create_navbar(config):
    navbar_layout = html.Nav(
        className="bg-blue-400",
        children=[
            # Brand and burger
            html.Div(
                className="px-2 mx-auto max-w-7xl sm:px-6 lg:px-8",
                children=[
                    html.Div(
                        className="relative flex items-center justify-between h-16",
                        children=[
                            # Mobile menu button
                            html.Button(
                                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white sm:hidden",
                                id="navbar-toggler",
                                children=[
                                    # Icon (using FontAwesome)
                                    html.I(className="fas fa-bars")
                                ],
                            ),
                            # Brand/logo
                            html.Div(
                                className="flex-shrink-0 flex items-center",
                                children=[
                                    html.Img(
                                        src=config["logo_path"],
                                        alt=config["brand_name"],
                                        className="block lg:hidden h-8 w-auto",
                                    ),
                                    html.Img(
                                        src=config["logo_path"],
                                        alt=config["brand_name"],
                                        className="hidden lg:block h-8 w-auto",
                                    ),
                                ],
                            ),
                            # Links for large screens
                            html.Div(
                                className="hidden sm:block sm:ml-6",
                                children=[
                                    html.Div(
                                        className="flex space-x-4",
                                        children=[
                                            html.A(
                                                href=page["path"],
                                                className="px-3 py-2 rounded-md text-sm font-medium text-gray-800 hover:text-white hover:bg-gray-700",
                                                children=page["name"],
                                            )
                                            for page in config["pages"]
                                        ],
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Mobile menu (hidden by default)
            html.Div(
                className="sm:hidden",
                id="navbar-collapse",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="px-2 pt-2 pb-3 space-y-1",
                        children=[
                            html.A(
                                href=page["path"],
                                className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700",
                                children=page["name"],
                            )
                            for page in config["pages"]
                        ],
                    )
                ],
            ),
        ],
    )

    return navbar_layout


# Define callback for toggling the mobile menu
def register_navbar_callbacks(app:Dash):
    @app.callback(
        Output("navbar-collapse", "style"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "style")],
    )
    def toggle_navbar_collapse(n, style):
        if n and n > 0:
            if style and style.get("display") == "none":
                return {"display": "block"}
            else:
                return {"display": "none"}
        return style


# this config template will be used to create the navbar
config = {
    "brand_name": "Dash App",
    "logo_path": "assets/logo.png",
    "pages": [
        {"name": "Home", "path": "/"},
        {"name": "About", "path": "/about"},
        {"name": "Documentation", "path": "/docs"},
    ],
}
