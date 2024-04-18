import dash
import dash_bootstrap_components as dbc
from dash import html


def create_sidebar(app_title):
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    app_title, href="/"
                ),
                    dbc.Nav(
                        [
                            dbc.NavLink(
                                html.Div(page["name"], className="sidebar-text"),
                                href=page["path"],
                                active="exact",
                            )
                            for page in dash.page_registry.values()
                        ],
                        className="ms-auto",
                        navbar=True,
                        pills=True,
                    ),
            ],
            fluid=True,
        ),
        className="mb-4",
    )
