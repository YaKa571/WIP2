import dash_bootstrap_components as dbc
from dash import html

from frontend.component_ids import IDs

TABS = [
    ("Home", IDs.TAB_HOME.value),
    ("Fraud", IDs.TAB_FRAUD.value),
    ("Cluster", IDs.TAB_CLUSTER.value),
    ("User", IDs.TAB_USER.value),
    ("Merchant", IDs.TAB_MERCHANT.value),
]


def create_tabs():
    """
    Creates a custom tab bar with buttons for each defined tab in TABS.

    This function dynamically generates a tab bar using a list of predefined
    tab configurations from TABS. Each button in the tab bar corresponds to a
    tab, with specific labels and identifiers. The buttons are styled and
    initialized with a default click count of zero ('n_clicks').

    Returns:
        Div: A Dash HTML Div component containing the tab buttons.

    """
    buttons = []
    for label, tid in TABS:
        buttons.append(
            dbc.Button(
                label,
                id={"type": "custom-tab", "index": tid},
                n_clicks=0,
                className="custom-tab-button"
            )
        )

    return html.Div(
        buttons,
        className="d-flex custom-tab-bar"
    )


def create_right_column():
    """
    Creates the right-hand column layout of the page.

    This function composes the layout structure for the right-hand column
    using Dash and Dash Bootstrap Components. The content includes a card
    that contains tabs and a dynamic content area.

    Returns
    -------
    dash.html.Div
        A Div component structured as the right-hand column of the page.
    """
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        create_tabs(),
                        html.Div(id="custom-tab-content", className="tab-content-wrapper flex-fill")
                    ],
                    className="d-flex flex-column p-0"
                ),
                className="card h-100"
            )
        ],
        className="right-column"
    )
