import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
from plotly.graph_objs._figure import Figure

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()
PIE_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False
}
COLOR_BLUE_MAIN = "#0d6efd"
BAR_CHART_OPTIONS = [
    {"label": "MOST VALUABLE MERCHANTS", "value": "most_valuable_merchants"},
    {"label": "MOST VISITED MERCHANTS", "value": "most_visited_merchants"},
    {"label": "TOP SPENDING USERS", "value": "top_spending_users"},
    {"label": "PEAK HOUR", "value": "peak_hour"},
]


# TODO: @Diego
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
    return html.Div(children=[

        _create_heading(),
        _create_top_kpis(),
        _create_middle_circle_diagrams(),
        _create_bottom_bar_diagrams()

    ],
        className="tab-content-inner"
    )


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
        children=[

            html.Button(children=[
                html.I(className="bi bi-geo-alt-fill me-2"),
                "Show all States"
            ]
                , className="settings-button-text hidden",
                id=ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES),
            html.H4(
                "All States",
                id=ID.HOME_TAB_STATE_HEADING
            ),
            comp_factory.create_info_icon(ID.HOME_TAB_INFO_ICON),
            dbc.Tooltip(children=[
                "Click on any State on",
                html.Br(),
                "the map to update the",
                html.Br(),
                "charts and KPIs"
            ],
                target=ID.HOME_TAB_INFO_ICON,
                is_open=False,
                placement="bottom-end"
            )

        ],
        className="tab-home-heading-wrapper"
    )


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
    return html.Div(children=[

        html.Div(children=[

            # KPI 1: Most Value Merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[

                    comp_factory.create_icon(IconID.TROPHY, cls="icon icon-small"),
                    html.P("Most Valuable Merchant", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.HOME_KPI_MOST_VALUABLE_MERCHANT
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",

                )

            ],
                className="card kpi-card",
            ),

            # KPI 2: Most Visited Merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[

                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("Most Visited Merchant", className="kpi-card-title"),

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading([
                        html.Div(children=[

                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")

                        ],
                            id=ID.HOME_KPI_MOST_VISITED_MERCHANT
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body"
                )

            ],
                className="card kpi-card",
            ),

            # KPI 3: Top Spending User
            dbc.Card(children=[
                dbc.CardHeader(children=[

                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P(children="Top Spending User", className="kpi-card-title"),

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.HOME_KPI_TOP_SPENDING_USER
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",

                )
            ],
                className="card kpi-card",
            ),

            # KPI 4: Peak Hour
            dbc.Card(children=[
                dbc.CardHeader(children=[

                    comp_factory.create_icon(IconID.TIME, cls="icon icon-small"),
                    html.P(children="Peak Hour", className="kpi-card-title"),

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.HOME_KPI_PEAK_HOUR
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",

                )
            ],
                className="card kpi-card",
            ),

        ],
            className="flex-wrapper"
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
    return html.Div(children=[

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.GENDERS, cls="icon icon-small"),
                html.P(children="Expenditures by Gender", className="graph-card-title"),

            ],
                className="card-header"),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_GENDER,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )

                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)
            ])

        ],
            className="card graph-card"),

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.CART, cls="icon icon-small"),
                html.P(children="Expenditures by Channel", className="graph-card-title"),

            ],
                className="card-header"),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )

                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)
            ])

        ],
            className="card graph-card"),

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.CAKE, cls="icon icon-small"),
                html.P(children="Expenditures by Age", className="graph-card-title"),

            ],
                className="card-header"
            ),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_AGE,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )
                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)

            ])

        ],
            className="card graph-card"),

    ],
        className="flex-wrapper"
    )


def _create_bottom_bar_diagrams() -> html.Div:
    return html.Div(children=[

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.BAR_CHART_LINE_FILL, cls="icon icon-small"),
                html.Div(children=[
                    dcc.Dropdown(className="settings-dropdown settings-text-centered",
                                 options=BAR_CHART_OPTIONS,
                                 id=ID.HOME_TAB_BAR_CHART_DROPDOWN,
                                 placeholder="Select a KPI...",
                                 style={"width": "100%"},
                                 value=BAR_CHART_OPTIONS[0]["value"],
                                 clearable=False
                                 ),
                ],
                    className="settings-item mt-2")
            ]
            ),

            dbc.CardBody(children=[

                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="bar-chart",
                        id=ID.HOME_GRAPH_BAR_CHART,
                        config={"responsive": True},
                        responsive=True,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )
                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)

            ])
        ],
            className="graph-card")

    ],
        className="flex-wrapper flex-fill")


def create_pie_graph(data: dict, colors=None, textinfo: str = "percent+label", showlegend: bool = True,
                     dark_mode: bool = False) -> go.Figure:
    """
    Create a pie graph visualization.

    This function generates a pie chart visualization using the given data.
    It allows customization of colors, text information display, legend visibility,
    and a dark mode for the chart appearance.

    Arguments:
        data: dict
            A dictionary containing labels as keys and corresponding values as values
            for the pie chart sections.
        colors: list, optional
            A list of colors for the pie slices. Defaults to ["#c65ed4", "#5d9cf8"].
        textinfo: str, optional
            String specifying which text elements to show on the chart (e.g., 'percent+label').
            Defaults to "percent+label".
        showlegend: bool, optional
            Determines whether to display the legend on the chart. Defaults to True.
        dark_mode: bool, optional
            Configures text color and background appearance for dark mode. Defaults to False.

    Returns:
        go.Figure
            A Plotly Figure object representing the pie chart visualization.
    """
    if colors is None:
        colors = ["#c65ed4", "#5d9cf8"]  # Female = pink, Male = blue

    textcolor = "white" if dark_mode else "black"

    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(
        data=[go.Pie(
            name="",
            labels=labels,
            values=values,
            hole=0.42,
            marker=dict(colors=colors),
            textinfo=textinfo,
            textfont=dict(color=textcolor),
            hovertemplate="%{label}<br>%{percent}<br>$%{value:,.2f}"
        )],
        layout=go.Layout(
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=showlegend
        )
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            x=1,  # 100% right
            y=1,  # 100% top
            xanchor="right",
            yanchor="top",
            font=dict(size=12, color="#0d6efd", weight="bold")
        )
    )

    return fig


def get_most_valuable_merchant_details(state: str = None) -> list:
    """
    Fetches and generates HTML components that display the most valuable merchant's
    details. The function retrieves the most profitable merchant's description and
    value for a given state, wraps them in HTML components, and returns them as
    elements in a list.

    Parameters:
        state (str, optional): The state for which the most valuable merchant's
        information should be retrieved. Defaults to None.

    Returns:
        list: A list containing two HTML components. The first component displays
        the merchant's description, and the second displays the monetary value
        associated with the merchant.

    """
    one = html.P(
        f"{dm.get_most_valuable_merchant(state).mcc_desc}",
        className="kpi-card-value")
    two = html.P(f"${dm.get_most_valuable_merchant(state).value}",
                 className="kpi-card-value kpi-number-value")
    tooltip = dbc.Tooltip(children=[
        f"Merchant ID: {dm.get_most_valuable_merchant(state).id}",
        html.Br(),
        f"MCC: {dm.get_most_valuable_merchant(state).mcc}"
    ],
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_1"},
        target=ID.HOME_KPI_MOST_VALUABLE_MERCHANT
    )

    return [one, two, tooltip]


def get_most_visited_merchant_details(state: str = None) -> list:
    """
    Fetches and returns the details of the most visited merchant for a given state.

    The function retrieves details of the most visited merchant, such as the merchant's
    description and the number of visits, and formats them as HTML components.

    Parameters:
        state (str, optional): The state for which the most visited merchant's
        details are to be fetched. Defaults to None.

    Returns:
        list: A list containing two HTML components. The first component includes the
        description of the most visited merchant, and the second component includes
        the number of visits.
    """
    one = html.P(
        f"{dm.get_most_visited_merchant(state).mcc_desc}",
        className="kpi-card-value")
    two = html.P(f"{dm.get_most_visited_merchant(state).visits} visits",
                 className="kpi-card-value kpi-number-value")
    tooltip = dbc.Tooltip(children=[
        f"Merchant ID: {dm.get_most_visited_merchant(state).id}",
        html.Br(),
        f"MCC: {dm.get_most_visited_merchant(state).mcc}"
    ],
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_2"},
        target=ID.HOME_KPI_MOST_VISITED_MERCHANT
    )
    return [one, two, tooltip]


def get_top_spending_user_details(state: str = None) -> list:
    """
    Retrieves details of the top spending user in a given state. This function fetches the
    top spending user's details, such as gender, age, and spending value, formats them
    into presentable components, and returns them as a list.

    Parameters:
    state: str, optional
        The state for which to retrieve the top spending user details. If not provided,
        data is fetched for all states.

    Returns:
    list
        A list of top spending user details, including formatted gender, age, and
        spending value.
    """
    one = html.P(
        f"{dm.get_top_spending_user(state).gender}, {dm.get_top_spending_user(state).current_age} years",
        className="kpi-card-value")
    two = html.P(f"${dm.get_top_spending_user(state).value}",
                 className="kpi-card-value kpi-number-value")
    tooltip = dbc.Tooltip(children=[
        f"User ID: {dm.get_top_spending_user(state).id}"
    ],
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_3"},
        target=ID.HOME_KPI_TOP_SPENDING_USER
    )
    return [one, two, tooltip]


def get_peak_hour_details(state: str = None) -> list:
    """
    Fetches and returns the details of peak hour metrics for a given state. This includes
    the hour range during which peak activity occurs and the number of transactions
    recorded during that period. The function constructs HTML components containing
    these details for consistent rendering in the application.

    Args:
        state (str, optional): The state identifier for which peak hour details are
            requested. Defaults to None.

    Returns:
        list: A list of HTML paragraph elements containing the peak hour range and the
            transaction count information.
    """
    one = html.P(
        f"{dm.get_peak_hour(state).hour_range}",
        className="kpi-card-value")
    two = html.P(f"{dm.get_peak_hour(state).value} transactions",
                 className="kpi-card-value kpi-number-value")

    return [one, two]


def get_most_valuable_merchant_bar_chart(state: str = None):
    df = dm.get_merchant_values_by_state(state=state).head(10)

    fig = px.bar(df,
                 x="mcc",
                 y="merchant_sum",
                 hover_data=["mcc_desc", "merchant_id"],
                 )

    # Handle x-axis values as category as they're numerical
    fig.update_xaxes(type="category")

    # Sort categories -> merchant_sum descending
    fig.update_layout(xaxis=dict(categoryorder="total descending"),
                      margin=dict(l=0, t=0, r=0, b=0))

    # Set bar color
    fig.update_traces(marker_color=COLOR_BLUE_MAIN)

    return fig
