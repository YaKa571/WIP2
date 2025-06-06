import dash_bootstrap_components as dbc
from dash import html, dcc

import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()

# Constants for configuration
MODEBAR_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False
)

BAR_CHART_OPTIONS = [
    {"label": "TOTAL AMOUNT", "value": "amount"},
    {"label": "TRANSACTION COUNT", "value": "count"},
]


def create_user_content() -> html.Div:
    """
    Creates the user content section of a web application using Dash framework.

    This function generates a Dash HTML Div component with class name 'tab-content-inner
    user-tab' that serves as the container for various subsections such as headings,
    search bars, KPIs, and diagrams. The function utilizes private helper functions to
    assemble each subsection.

    Returns:
        dash_html_components.Div: A Dash HTML Div that contains the user content layout.
    """
    return html.Div(
        className="tab-content-inner user-tab",
        children=[

            _create_heading(),
            _create_search_bars(),
            _create_top_kpis(),
            _create_credit_limit_kpi(),
            _create_bottom_merchant_diagram()

        ])


def _create_heading() -> html.Div:
    """
    Creates a heading component for a user or card tab.

    This function generates a heading component for the user or card tab, including a title, an
    information icon, and a tooltip describing the purpose of the tab. The tooltip offers guidance
    on how to update information for a selected user or card.

    Returns:
        html.Div: A Dash HTML Div element representing the tab heading, including the title, an
                  information icon, and an associated tooltip.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element for spacing
            html.H4("User", id=ID.USER_TAB_HEADING, className="green-text"),
            comp_factory.create_info_icon(ID.USER_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.USER_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Enter a User ID or",
                    html.Br(),
                    "Card ID to update the",
                    html.Br(),
                    "information for the selected",
                    html.Br(),
                    "user or card"
                ])

        ])


def _create_search_bars() -> html.Div:
    """
    Creates a section with two search bars for user ID and card ID.

    Returns
    -------
    html.Div
        A Div element containing two search bars with magnifier icons.
    """
    unique_cards = dm.user_tab_data.unique_card_ids
    min_card_id = min(unique_cards)
    max_card_id = max(unique_cards)

    unique_users = dm.user_tab_data.unique_user_ids
    min_user_id = min(unique_users)
    max_user_id = max(unique_users)

    return html.Div(
        className="flex-wrapper",
        children=[

            _create_single_search_bar(ID.USER_ID_SEARCH_INPUT, f"SEARCH BY USER ID ({min_user_id} - {max_user_id})",
                                      start_value=1098,
                                      min_value=min_user_id, max_value=max_user_id),

            _create_single_search_bar(ID.CARD_ID_SEARCH_INPUT, f"SEARCH BY CARD ID ({min_card_id} - {max_card_id})",
                                      min_value=min_card_id, max_value=max_card_id)

        ])


def _create_single_search_bar(input_id: str, placeholder: str, start_value: int = None, min_value: int = 0,
                              max_value: int = 9_999_999) -> dcc.Input:
    """
    Creates a single search bar input element with the specified id, placeholder text, and optional start value. This
    component is constructed as a Dash Core Components Input element with the "search" type, designed for user input
    related to search functionality.

    Args:
        input_id: A unique identifier for the search bar input element.
        placeholder: A textual hint for the user indicating the intended input value.
        start_value: An optional initial value to populate the search bar.

    Returns:
        A Dash Core Components Input element configured as a search bar.
    """
    return dcc.Input(
        id=input_id,
        value=start_value,
        type="number",
        min=min_value,
        max=max_value,
        autoComplete="off",
        placeholder=placeholder,
        className="search-bar-input no-spinner"
    )


def _create_top_kpis() -> html.Div:
    """
    Creates a row of four KPI boxes for the selected user or card.
    The values update when a User ID or Card ID is entered.

    Returns
    -------
    html.Div
        A Div element containing four KPI boxes in a flex layout.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            # KPI Transaction Count
            comp_factory.create_kpi_card(
                icon_id=IconID.CHART_PIPE,
                title="Transactions",
                div_id=ID.USER_KPI_TX_COUNT
            ),

            # KPI Transaction Sum
            comp_factory.create_kpi_card(
                icon_id=IconID.MONEY_DOLLAR,
                title="Total Sum",
                div_id=ID.USER_KPI_TX_SUM
            ),

            # KPI Average Transaction
            comp_factory.create_kpi_card(
                icon_id=IconID.CHART_AVERAGE,
                title="Average Amount",
                div_id=ID.USER_KPI_TX_AVG
            ),

            # KPI Card Count
            comp_factory.create_kpi_card(
                icon_id=IconID.CREDITCARD,
                title="Credit Cards",
                div_id=ID.USER_KPI_CARD_COUNT
            ),

        ])


def _create_credit_limit_kpi() -> html.Div:
    """
    Creates the KPI card container for displaying the credit limit information.

    This function creates a container that is structured with a
    KPI card widget for displaying the user's credit limit.
    It includes an icon, title, and a styled container layout.

    Returns:
        Div: A Dash HTML Div element configured with the credit limit
             KPI card.
    """
    return html.Div(
        className="flex-wrapper",
        children=[
            dbc.Card(
                className="kpi-card kpi-credit-limit-card",
                children=[
                    dbc.CardHeader(
                        children=[
                            comp_factory.create_icon(IconID.MONEY_DOLLAR, cls="icon icon-small"),
                            html.P("Credit Limit Breakdown", className="kpi-card-title"),
                        ],
                        className="card-header fit-content"
                    ),
                    dbc.CardBody(
                        children=[

                            html.Div(id=ID.USER_CREDIT_LIMIT_BOX, className="kpi-card-value kpi-number-value"),
                            html.Div(
                                className="credit-limit-bar-wrapper",
                                children=[

                                    dcc.Graph(
                                        id=ID.USER_CREDIT_LIMIT_BAR,
                                        config={"displayModeBar": False},
                                        style={
                                            "height": "100%", "width": "100%",
                                        }
                                    )
                                ])
                        ],
                        className="card-body fit-content"
                    )
                ]
            )
        ]
    )


def _create_bottom_merchant_diagram() -> html.Div:
    """
    Creates the merchant bar chart section with a dropdown for sorting options.

    Returns
    -------
    html.Div
        A Div element containing a dropdown and a bar chart in a flex layout.
    """
    return html.Div(
        className="flex-wrapper flex-fill",
        children=[

            dbc.Card(
                className="graph-card with-bar-chart",
                children=[

                    dbc.CardHeader(
                        children=[

                            html.Div(
                                className="settings-item",
                                children=[

                                    dcc.Dropdown(
                                        className="settings-dropdown settings-text-centered",
                                        id=ID.USER_MERCHANT_SORT_DROPDOWN,
                                        placeholder="Select sorting...",
                                        style={"width": "100%"},
                                        value="amount",
                                        clearable=False,
                                        searchable=False,
                                        options=BAR_CHART_OPTIONS
                                    )
                                ])
                        ]),

                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                figure=comp_factory.create_empty_figure(),
                                className="bar-chart",
                                config=MODEBAR_CONFIG,
                                id=ID.USER_MERCHANT_BAR_CHART,
                                responsive=True,
                                style={
                                    "height": "100%",
                                    "minHeight": 0,
                                    "minWidth": 0
                                }
                            ),

                            html.Div(className="map-spinner visible", id=ID.USER_BAR_CHART_SPINNER),

                            comp_factory.create_info_icon(
                                icon_id=ID.USER_TAB_BAR_INFO_ICON,
                                style={
                                    "position": "absolute",
                                    "top": "80px",
                                    "left": "16px",
                                    "zIndex": 100
                                }),

                            dbc.Tooltip(
                                target=ID.USER_TAB_BAR_INFO_ICON,
                                is_open=False,
                                placement="right",
                                children=[
                                    "Click any bar to explore",
                                    html.Br(),
                                    "further information"
                                ])

                        ])
                ])
        ])


def create_kpi_value_text(text: str, red_text_color: bool = False) -> html.P:
    """
    Generates an HTML paragraph element with a class for styling KPI values.

    This function creates an HTML paragraph element with a specific CSS class
    depending on whether the text is to be displayed in red or not. The generated
    paragraph is commonly used for presenting KPI (Key Performance Indicator)
    values in a styled manner.

    Args:
        text: The text content to be displayed within the HTML paragraph.
        red_text_color: Specifies whether the text should be styled with a red
            text color. Defaults to False.

    Returns:
        An html.P object styled based on the specified parameters.
    """
    className = "kpi-card-value kpi-number-value" if not red_text_color else "kpi-card-value kpi-number-value info-text"
    return html.P(text, className=className)
