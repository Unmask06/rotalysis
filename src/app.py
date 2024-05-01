"""app.py - Main file for the Rotalyis app."""


from agility.skeleton.custom_components import NavbarCustom
from dash import Dash, html, page_container

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.15.4/js/all.js"
TAILWIND = "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[TAILWIND, FONT_AWESOME],
)

app.title = "Rotalysis"

app.layout = html.Div(
    [
        NavbarCustom(app.title).layout,
        page_container,
    ]
)


if __name__ == "__main__":
    app.run(debug=True, port="80")
    # app.run(host="10.29.3.31", port="80")
