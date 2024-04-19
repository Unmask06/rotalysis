from dash import html


def create_cards(config):
    cards = html.Ul(
        role="list",
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 p-10",
        children=[
            html.Li(
                className="col-span-1 divide-y divide-gray-300 rounded-lg bg-white shadow-lg",  # Adjusted shadow and divide color
                children=[
                    # Card content without image
                    html.Div(
                        className="p-6",
                        children=[
                            html.Div(
                                className="flex-1",
                                children=[
                                    html.H3(
                                        className="text-lg font-semibold text-gray-900",  # Increased font size
                                        children=item["topic"],
                                    ),
                                    html.P(
                                        className="mt-2 text-sm text-gray-500",  # Adjusted margin and text size
                                        children=item.get("description", ""),
                                    ),
                                ],
                            ),
                            # Link at the bottom of the card
                            html.Div(
                                className="mt-4 flex divide-x divide-gray-200",  # Adjusted margin
                                children=[
                                    html.A(
                                        href=item["page_path"],
                                        className="inline-flex w-full items-center justify-center gap-x-3 rounded-md border border-transparent py-2 text-base font-semibold text-gray-900 hover:bg-gray-100",  # Adjusted padding, text size, and hover effect
                                        children=[
                                            html.I(
                                                className="fas fa-arrow-right h-5 w-5 text-gray-400"
                                            ),
                                            "Go To",
                                        ],
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            )
            for item in config["items"]
        ],
    )
    return cards


config = {
    "items": [
        {
            "topic": "Jane Cooper",
            "description": "Regional Paradigm Technician",
            "page_path": "/jane-cooper-profile",
        },
        # More items can be added here
    ]
}
