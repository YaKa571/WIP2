import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html, dcc
from plotly.graph_objs._figure import Figure

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()

MODEBAR_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False
)
COLOR_BLUE_MAIN = "#2563eb"
FEMALE_PINK = "#c65ed4"
BAR_CHART_OPTIONS = [
    {"label": "MOST VALUABLE MERCHANTS", "value": "most_valuable_merchants"},
    {"label": "MOST VISITED MERCHANTS", "value": "most_visited_merchants"},
    {"label": "TOP SPENDING USERS", "value": "top_spending_users"},
    {"label": "PEAK HOURS", "value": "peak_hours"},
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

            html.H4("All States", id=ID.HOME_TAB_STATE_HEADING),
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
                title="Expenditures by Gender",
                graph_id=ID.HOME_GRAPH_EXPENDITURES_BY_GENDER,
            ),

            # Pie Chart Expenditures by Channel
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.CART,
                title="Expenditures by Channel",
                graph_id=ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL,
            ),

            # Pie Chart Expenditures by Age
            comp_factory.create_circle_diagram_card(
                icon_id=IconID.CAKE,
                title="Expenditures by Age",
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

                            comp_factory.create_icon(IconID.BAR_CHART_LINE_FILL, cls="icon icon-small"),
                            html.Div(
                                className="settings-item mt-2",
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
                                    "minHeight": 0,
                                    "minWidth": 0
                                }
                            )

                        ])
                ])

        ])


def create_pie_graph(data: dict, colors=None, textinfo: str = "percent+label",
                     hover_template: str = None, showlegend: bool = True,
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
        colors = [FEMALE_PINK, COLOR_BLUE_MAIN]  # Female = pink, Male = blue

    textcolor = "white" if dark_mode else "black"

    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(
        data=[
            go.Pie(
                name="",
                labels=labels,
                values=values,
                hole=0.42,
                marker=dict(colors=colors),
                textinfo=textinfo,
                textfont=dict(color=textcolor),
                hovertemplate=hover_template
            )
        ],
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

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_1"},
        target=ID.HOME_KPI_MOST_VALUABLE_MERCHANT,
        children=[
            f"🆔 Merchant ID: {dm.get_most_valuable_merchant(state).id}",
            html.Br(),
            f"🏷️ MCC: {dm.get_most_valuable_merchant(state).mcc}"
        ])

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

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_2"},
        target=ID.HOME_KPI_MOST_VISITED_MERCHANT,
        children=[
            f"🆔 Merchant ID: {dm.get_most_visited_merchant(state).id}",
            html.Br(),
            f"🏷️MCC: {dm.get_most_visited_merchant(state).mcc}"
        ])

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

    two = html.P(f"${dm.get_top_spending_user(state).value}", className="kpi-card-value kpi-number-value")

    tooltip = dbc.Tooltip(
        placement="bottom",
        is_open=False,
        trigger="hover",
        id={"type": "tooltip", "id": "tab_home_kpi_3"},
        target=ID.HOME_KPI_TOP_SPENDING_USER,
        children=[
            f"🆔 User ID: {dm.get_top_spending_user(state).id}"
        ])

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
    one = html.P(f"{dm.get_peak_hour(state).hour_range}", className="kpi-card-value")
    two = html.P(f"{dm.get_peak_hour(state).value} transactions", className="kpi-card-value kpi-number-value")

    return [one, two]


def get_most_valuable_merchant_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generates a bar chart to visualize the top 10 most valuable merchants based on their total
    transaction values for a given state or all states.

    This function retrieves the merchant transaction values, sorts them, and selects the top
    10 merchants. It then generates a bar chart displaying the Merchant Category Code (MCC)
    against the total transaction values. Additional information such as merchant descriptions
    and IDs is available as hover data. The chart's appearance can be customized for light or
    dark mode rendering.

    Parameters:
        state (str, optional): The state code for which the top merchants are to be analyzed. If not
                               specified, the analysis includes all states.
        dark_mode (bool, optional): Determines the visual style of the chart. If True, the chart
                                    is displayed in dark mode. Defaults to False.

    Returns:
        plotly.graph_objects.Figure: A bar chart displaying the top 10 most valuable merchants
                                      for the specified state, or across all states when no state
                                      is provided.
    """
    df = dm.get_merchant_values_by_state(state=state).head(10)

    hover_template = (
        "🏷️ <b>MCC:</b> %{x}<br>"
        "📝 <b>Description:</b> %{customdata[0]}<br>"
        "🆔 <b>Merchant ID:</b> %{customdata[1]}<br>"
        "💰 <b>Sum:</b> $%{y:,.2f}<br>"
        "<extra></extra>"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="mcc",
        y="merchant_sum",
        custom_data=["mcc_desc", "merchant_id"],
        hover_template=hover_template,
        title=f"TOP 10 MOST VALUABLE MERCHANTS IN {state.upper() if state else 'ALL STATES'}",
        labels={"mcc": "MCC", "merchant_sum": "Sum"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )


def get_peak_hour_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Returns a bar chart visualizing the peak transaction hours for a specific state
    or for all states if no state is specified.

    The function retrieves transaction counts grouped by hour from the database
    and filters out hours with zero transactions. It formats the hour data
    to display as a range ("HH – HH") and creates a bar chart using
    this processed data. The color scheme of the chart can be adjusted
    by specifying the dark_mode parameter.

    Parameters:
        state: str, optional
            The specific state for which transaction data is to be visualized.
            Defaults to None, in which case data for all states is used.
        dark_mode: bool, optional
            A flag to determine if the chart should use a dark color scheme.
            Defaults to False.

    Returns:
        plotly.graph_objects.Figure
            A bar chart displaying the number of transactions for each hour range.
    """
    df = dm.get_transaction_counts_by_hour(state=state)
    df = df[df["transaction_count"] > 0].copy()
    df["hour_range"] = df["hour"].apply(lambda h: f"{h:02d}:00 – {(h + 1) % 24:02d}:00")

    hover_template = (
        "⏰ <b>Hour:</b> %{customdata[0]}<br>"
        "💳 <b>Transactions:</b> %{customdata[1]:,}<br>"
        "<extra></extra>"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="hour_range",
        y="transaction_count",
        custom_data=["hour_range", "transaction_count"],
        hover_template=hover_template,
        title=f"MOST ACTIVE HOURS IN {state.upper() if state else 'ALL STATES'}",
        labels={"hour_range": "Hour Range", "transaction_count": "Number of Transactions"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )


def get_spending_by_user_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generate a bar chart visualizing the top 10 most spending users. Users can be filtered by state, and the chart
    supports dark mode styling.

    Arguments:
        state (str, optional): The state for which the top users should be filtered. If not provided, includes all states.
        dark_mode (bool, optional): Determines whether the bar chart should be rendered in dark mode. Defaults to False.

    Returns:
        Bar chart visualization showcasing the top 10 spending users, with data categorized by gender and additional
        hover information such as gender, age, and spending.
    """
    df = dm.get_spending_by_user(state).head(10)
    df = df.merge(dm.df_users[["id", "gender", "current_age"]], left_on="client_id", right_on="id").drop(columns=["id"])

    hover_template = (
        "🆔 <b>User ID:</b> %{x}<br>"
        "🧑‍🤝‍🧑 <b>Gender:</b> %{customdata[0]}<br>"
        "🎂 <b>Age:</b> %{customdata[1]}<br>"
        "💸 <b>Spending:</b> $%{customdata[2]:,.2f}<br>"
        "<extra></extra>"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="client_id",
        y="spending",
        color="gender",
        color_discrete_map={"Female": FEMALE_PINK, "Male": COLOR_BLUE_MAIN},
        custom_data=["gender", "current_age", "spending"],
        hover_template=hover_template,
        title=f"TOP 10 MOST SPENDING USERS IN {state.upper() if state else 'ALL STATES'}",
        labels={"client_id": "User ID", "spending": "Total Spending", "gender": "Gender", "current_age": "Age"},
        showlegend=True,
        dark_mode=dark_mode
    )


def get_most_visited_merchants_bar_chart(state: str = None, dark_mode: bool = False):
    """
    Generates a bar chart visualization for the top 10 most visited merchants. The chart
    displays merchant IDs on the x-axis and the number of visits on the y-axis, with
    additional hover data for merchant category code (MCC) and description. The state
    can be optionally specified to filter data for a specific region.

    Args:
        state (str, optional): The state for which to filter the merchant data.
            If None, data from all states is used. Defaults to None.
        dark_mode (bool, optional): Determines the color scheme of the chart. If True,
            the chart will use a dark theme. Defaults to False.

    Returns:
        A bar chart representation of the top 10 most visited merchants based on the
        specified parameters.
    """
    df = dm.get_visits_by_merchant(state).head(10)

    hover_template = (
        "🏷️ <b>MCC:</b> %{customdata[0]}<br>"
        "📝 <b>Description:</b> %{customdata[1]}<br>"
        "🆔 <b>Merchant ID:</b> %{x}<br>"
        "👣 <b>Visits:</b> %{customdata[2]:,}<br>"
        "<extra></extra>"
    )

    return comp_factory.create_bar_chart(
        df=df,
        x="merchant_id",
        y="visits",
        custom_data=["mcc", "mcc_desc", "visits"],
        hover_template=hover_template,
        title=f"TOP 10 MOST VISITED MERCHANTS IN {state.upper() if state else 'ALL STATES'}",
        labels={"merchant_id": "Merchant ID", "visits": "Visits"},
        bar_color=COLOR_BLUE_MAIN,
        dark_mode=dark_mode
    )
