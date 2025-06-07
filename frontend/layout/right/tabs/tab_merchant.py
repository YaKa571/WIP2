import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()


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
    Creates a heading component for a user interface with interactive elements such
    as a button, heading, info icon, and tooltip.

    Returns:
        html.Div: A Div component composed of interactive elements including a
        button to toggle all states, a heading for 'Merchant', an info icon for
        additional information, and a tooltip that provides usage instructions.

    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            html.Button(
                className="settings-button-text hidden",
                id=ID.MERCHANT_BTN_MAP,
                children=[

                    html.I(className="bi bi-geo-alt-fill me-2"),
                    "Show all States"

                ]),
            html.H4("Merchant", id=ID.MERCHANT_HEADING, className="green-text"),
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
    Creates a horizontal row of buttons used for navigation or action selection.

    The function generates a row of buttons wrapped inside a flexible container.
    Each button represents a specific category or group for merchant navigation.
    The buttons include icons for visual indication and descriptive text for clarity.

    Returns:
        html.Div: A div containing a row of buttons with specific IDs, classes,
        and child elements including icons and text.
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
    merchant_groups = dm.merchant_tab_data.get_all_merchant_groups()
    options = [{'label': group, 'value': group} for group in merchant_groups]
    default_value = merchant_groups[0] if merchant_groups else None
    unique_ids = dm.merchant_tab_data.unique_merchant_ids

    return html.Div(
        className="flex-wrapper",
        children=[

            # Merchant Group dropdown input
            html.Div(
                className="flex-wrapper",
                id=ID.MERCHANT_GROUP_INPUT_WRAPPER,
                style={"display": "none", "width": "100%"},
                children=[

                    dcc.Dropdown(
                        id=ID.MERCHANT_INPUT_GROUP_DROPDOWN,
                        className="settings-dropdown settings-text-centered",
                        options=options,
                        value=default_value,
                        placeholder="CHOOSE A MERCHANT GROUP...",
                        searchable=True,
                        clearable=False,
                        multi=False,
                        style={"width": "100%"}
                    ),

                ]

            ),

            # Individual Merchant ID input
            html.Div(
                className="flex-wrapper",
                id=ID.MERCHANT_INPUT_WRAPPER,
                style={"display": "none", "width": "100%"},
                children=[

                    dcc.Input(
                        id=ID.MERCHANT_INPUT_MERCHANT_ID,
                        className="search-bar-input no-spinner",
                        type="number",
                        autoComplete="off",
                        min=min(unique_ids) if unique_ids else 0,
                        max=max(unique_ids) if unique_ids else 9_999_999,
                        value=50783,
                        placeholder=f"ENTER MERCHANT ID BETWEEN {min(unique_ids)} AND {max(unique_ids)}...",
                        style={"width": "100%"}
                    )

                ]

            )

        ]
    )


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
    Creates a merchant graph user interface component.

    This function generates a Dash HTML Div component representing the UI for a
    merchant graph. The UI includes a card layout containing a bar chart. The
    graph is configured with specific options and default settings to enhance
    usability and provide a visually appealing display.

    The interface includes an icon, a title, and a spinner for loading states.
    The graph itself is interactive and supports exporting functionality,
    while some less relevant mode bar buttons are removed for cleaner
    interaction.

    Returns:
        dash.development.base_component.Component:
            A Dash HTML Div component representing the merchant graph UI.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            dbc.Card(
                id=ID.MERCHANT_GRAPH_CARD,
                className="graph-card with-bar-chart",
                children=[

                    dbc.CardHeader(
                        children=[

                            html.Div(
                                className="card-header-inline-wrapper",
                                children=[

                                    comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-xs"),
                                    html.P(id=ID.MERCHANT_GRAPH_TITLE, className="graph-card-title")

                                ]
                            )
                        ]
                    ),
                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                id=ID.MERCHANT_GRAPH_CONTAINER,
                                className="bar-chart",
                                figure=comp_factory.create_empty_figure(),
                                config={
                                    "scrollZoom": True,
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
                            ),

                            html.Div(className="map-spinner visible", id=ID.MERCHANT_BAR_CHART_SPINNER),

                        ]
                    )
                ]
            )
        ]
    )
