import dash_bootstrap_components as dbc
from dash import html

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID


# Info: Edit grid layout in assets/css/tabs.css


# TODO: Free...
def create_fraud_content():
    return html.Div(
        className="tab-content-inner fraud-tab",
        children=[

            _create_heading()

        ]
    )


def _create_heading() -> html.Div:
    """
    Generates a heading layout for the Fraud tab using Dash components.

    The layout includes a dummy placeholder, a header, an information icon, and a tooltip
    with additional information.

    Returns:
        html.Div: A Div element containing the structured layout for the Fraud tab heading.

    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element
            html.H4("Fraud", id=ID.FRAUD_TAB_HEADING, className="green-text"),
            comp_factory.create_info_icon(ID.FRAUD_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.FRAUD_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Placeholder for",
                    html.Br(),
                    "the tooltip",
                    html.Br(),
                    "..."
                ])

        ])
