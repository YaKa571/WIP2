import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.callbacks.tabs import tab_merchant_callbacks
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID


# Info: Edit grid layout in assets/css/tabs.css

def create_merchant_content():
    """
    Creates the main content container for the Merchant tab.
    """
    return html.Div(
        className="tab-content-inner merchant-tab",
        children=[

            _create_heading(),
            _create_button_row(),
            _create_merchant_input_container(),
            _create_merchant_kpi(),
            _create_merchant_graph()

        ])


def _create_heading() -> html.Div:
    """
    Creates a heading section for the tab layout.

    The heading consists of a title, an info icon, and a tooltip describing usage instructions
    for merchant-related actions within the application interface.

    Returns:
        html.Div: A Dash HTML Div component containing the structured heading elements.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element for spacing
            html.H4("Merchant", id=ID.MERCHANT_HEADING),
            comp_factory.create_info_icon(ID.MERCHANT_INFO_ICON),
            dbc.Tooltip(
                target=ID.MERCHANT_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Click on All Merchants",
                    html.Br(),
                    "to show Treemap of all Merchants",
                    html.Hr(),
                    "Click on Merchant Group",
                    html.Br(),
                    "and choose from Dropdown",
                    html.Hr(),
                    "Click on Merchant",
                    html.Br(),
                    "and type in Merchant ID"
                ]),
        ])


def _create_button_row() -> html.Div:
    """
    Creates a row of buttons wrapped inside an HTML div element. Each button is associated
    with a unique identifier and a specific label or icon to specify its purpose in a user interface.

    Returns
    -------
    html.Div
        A div element containing four buttons: All Merchants, Merchant Group, Merchant,
        and Map. Each button has a unique identifier and a corresponding icon and text.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            html.Button(
                className="settings-button-text option-btn",
                id=ID.MERCHANT_BTN_ALL_MERCHANTS,
                children=[

                    html.I(className="bi bi-shop me-2"),
                    "All Merchants"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.MERCHANT_BTN_MERCHANT_GROUP,
                children=[

                    html.I(className="bi bi-collection me-2"),
                    "Merchant Group"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT,
                children=[

                    html.I(className="bi bi-shop-window me-2"),
                    "Merchant"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.MERCHANT_BTN_MAP,
                children=[

                    html.I(className="bi bi-globe-americas me-2"),
                    "Map"

                ])

        ])


def _create_merchant_input_container():
    """
    Creates a container for merchant input fields in a flexible layout.

    This function constructs a container element that contains input fields
    for selecting merchant groups or individual merchant IDs. The container
    is styled as a flexible wrapper, and its child elements are dynamically
    hidden or displayed as required.

    Returns:
        The HTML Div element containing the merchant input fields, organized
        in a flexible wrapper structure for layout alignment.

    """
    return html.Div(
        className="flex-wrapper",
        children=[

            # Merchant Group dropdown input
            html.Div(
                className="flex-wrapper",
                children=[tab_merchant_callbacks.get_merchant_group_input()],
                id=ID.MERCHANT_GROUP_INPUT_WRAPPER,
                style={"display": "none", "width": "100%"}
            ),

            # Individual Merchant ID input
            html.Div(
                className="flex-wrapper",
                children=[tab_merchant_callbacks.get_merchant_id_input()],
                id=ID.MERCHANT_INPUT_WRAPPER,
                style={"display": "none", "width": "100%"}
            )

        ])


def _create_merchant_kpi() -> html.Div:
    """
    Creates a container for the merchant KPI section.

    This function generates a container element designed to encapsulate and
    display key performance indicators (KPIs) related to merchants. The resulting
    container is identified by a unique ID. It is used for rendering KPI elements
    within a structured layout.

    Returns:
        html.Div: A container element with a predefined ID for displaying merchant
        KPIs.
    """
    return html.Div(id=ID.MERCHANT_KPI_CONTAINER)


def _create_merchant_graph():
    """
    Creates a merchant graph component.

    The function constructs a Dash HTML Div element representing a UI section
    displaying a merchant graph. It uses Dash Bootstrap Components (DBC) and
    Dash Core Components (DCC) to organize and style the graph section. The
    returned component includes a card header with an icon and title, and a card
    body containing a bar chart rendered using Dash's graph component. The bar
    chart is configured with custom mode bar options.

    Returns:
        dash.html.Div: A Div component containing the merchant graph card.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            dbc.Card(
                className="graph-card with-bar-chart lower-modebar",
                children=[

                    dbc.CardHeader(
                        children=[

                            comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-small"),
                            html.H3(id=ID.MERCHANT_GRAPH_TITLE, className="graph-card-title")

                        ]
                    ),
                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                id=ID.MERCHANT_GRAPH_CONTAINER,
                                className="bar-chart",
                                config={
                                    "displayModeBar": True,
                                    "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d",
                                                               "zoomIn2d", "zoomOut2d", "autoScale2d",
                                                               "resetScale2d", "hoverClosestCartesian",
                                                               "hoverCompareCartesian", "toggleSpikelines",
                                                               "sendDataToCloud", "toggleHover", "resetViews",
                                                               "resetViewMapbox"],
                                    "modeBarButtonsToAdd": ["toImage"],
                                    "displaylogo": False
                                },
                                style={
                                    "height": "100%",
                                    "width": "100%"
                                }
                            )

                        ]
                    )
                ]
            )
        ]
    )
