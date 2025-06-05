import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()

# Constants for configuration
MODEBAR_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False
)

BAR_CHART_OPTIONS = [
    {"label": "MOST VALUABLE MERCHANTS", "value": "most_valuable_merchants"},
    {"label": "MOST VISITED MERCHANTS", "value": "most_visited_merchants"},
    {"label": "TOP SPENDING USERS", "value": "top_spending_users"},
    {"label": "PEAK HOURS", "value": "peak_hours"},
]


def create_home_content() -> html.Div:
    """
    Creates the main content structure for the home tab of a dashboard.

    The function composes and returns a primary content container for the home
    tab, which includes a heading, key performance indicators (KPIs),
    and circle diagram components. These elements are assembled into a
    single layout container styled for display in the tab content.

    Returns
    -------
    html.Div
        A Div element containing the formatted components for the home tab
        content.
    """
    return html.Div(
        className="tab-content-inner home-tab",
        children=[

            _create_heading(),
            _create_top_kpis(),
            _create_middle_circle_diagrams(),
            _create_bottom_bar_diagrams()

        ])


def _create_heading() -> html.Div:
    """
    Creates a heading section for the home tab of the application.

    The heading includes a title, a button labeled 'ALL STATES',
    an informational icon, and a tooltip. The header is styled
    according to the provided classes, and the tooltip describes
    the functionality to interact with the map for updating charts
    and KPIs based on selected states.

    Returns
    -------
    html.Div
        A Dash HTML Div element containing the heading structure for
        the home tab, including a title, button, an informational
        icon with an interactive tooltip, and necessary CSS classes.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.Button(
                className="settings-button-text hidden",
                id=ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES,
                children=[

                    html.I(className="bi bi-geo-alt-fill me-2"),
                    "Show all States"

                ]),

            html.H4("All States", id=ID.HOME_TAB_STATE_HEADING, className="green-text"),
            comp_factory.create_info_icon(ID.HOME_TAB_INFO_ICON),
            dbc.Tooltip(
                target=ID.HOME_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Click on any State on",
                    html.Br(),
                    "the map to update the",
                    html.Br(),
                    "charts and KPIs"
                ])

        ])


def _create_top_kpis() -> html.Div:
    """
    Creates a section of top key performance indicators (KPIs) in the form of cards.

    Each KPI card is represented using `dbc.Card` and organized into the following
    categories:
    1. Highest Value Merchant
    2. Most Frequent Merchant
    3. Highest Value User
    4. Most Frequent User

    Each card contains a header with the respective KPI label and a body displaying the
    KPI value.

    Returns:
        html.Div: A `Div` container element that wraps all the KPI cards with a
        specific class style for layout and styling consistency.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            # KPI Most Valuable Merchant
            comp_factory.create_kpi_card(
                icon_id=IconID.TROPHY,
                title="Most Valuable Merchant",
                div_id=ID.HOME_KPI_MOST_VALUABLE_MERCHANT
            ),

            # KPI Most Visited Merchant
            comp_factory.create_kpi_card(
                icon_id=IconID.REPEAT,
                title="Most Visited Merchant",
                div_id=ID.HOME_KPI_MOST_VISITED_MERCHANT
            ),

            # KPI Top Spending User
            comp_factory.create_kpi_card(
                icon_id=IconID.USER_PAYING,
                title="Top Spending User",
                div_id=ID.HOME_KPI_TOP_SPENDING_USER
            ),

            # KPI Peak Hour
            comp_factory.create_kpi_card(
                icon_id=IconID.TIME,
                title="Peak Hour",
                div_id=ID.HOME_KPI_PEAK_HOUR
            )

        ])


def _create_middle_circle_diagrams() -> html.Div:
    """
    Creates a component containing visual representations of expenditures by gender and
    expenditures by channel using pie chart graphs. The method returns a layout structure
    that is wrapped within an HTML `Div`.

    Returns:
        html.Div: A Div component containing two cards; each card includes
        a header and a body. The headers contain icons and titles, and the
        bodies include pie chart graphs for gender-based and channel-based
        expenditure data.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            # Pie Chart Expenditures by Gender
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.GENDERS,
                title=["Expenditures by", "Gender"],
                graph_id=ID.HOME_GRAPH_EXPENDITURES_BY_GENDER,
            ),

            # Pie Chart Expenditures by Channel
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.CART,
                title=["Expenditures by", "Channel"],
                graph_id=ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL,
            ),

            # Pie Chart Expenditures by Age
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.CAKE,
                title=["Expenditures by", "Age"],
                graph_id=ID.HOME_GRAPH_EXPENDITURES_BY_AGE,
            )

        ])


def _create_bottom_bar_diagrams() -> html.Div:
    """
    Creates a bottom bar diagram component.

    This function generates a layout for a bottom bar diagram using Dash and Dash Bootstrap
    Components. It includes a card with a dropdown for selecting KPIs and a loading component
    that displays a bar chart. The bar chart is customizable with provided options and is
    styled for responsiveness.

    Returns:
        html.Div: A Dash HTML Div containing the entire layout for the bottom bar diagram.
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
                                        options=BAR_CHART_OPTIONS,
                                        id=ID.HOME_TAB_BAR_CHART_DROPDOWN,
                                        placeholder="Select a KPI...",
                                        style={"width": "100%"},
                                        value=BAR_CHART_OPTIONS[0]["value"],
                                        clearable=False,
                                        searchable=False,
                                    )

                                ])
                        ]),

                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                figure=comp_factory.create_empty_figure(),
                                className="bar-chart",
                                config=MODEBAR_CONFIG,
                                id=ID.HOME_GRAPH_BAR_CHART,
                                responsive=True,
                                style={
                                    "height": "100%",
                                    "width": "100%",
                                    "minHeight": 0,
                                    "minWidth": 0
                                }
                            ),

                            comp_factory.create_info_icon(
                                icon_id=ID.HOME_TAB_BAR_INFO_ICON,
                                style={
                                    "position": "absolute",
                                    "top": "80px",
                                    "left": "16px",
                                    "zIndex": 100
                                }),

                            dbc.Tooltip(
                                target=ID.HOME_TAB_BAR_INFO_ICON,
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
