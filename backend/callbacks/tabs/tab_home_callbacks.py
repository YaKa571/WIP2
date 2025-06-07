from dash import callback, Output, Input, ctx, no_update, State, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import components.constants as const
from backend.callbacks.tabs.tab_merchant_callbacks import ID_TO_MERCHANT_TAB
from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_home_data import HomeTabData
from components.constants import (
    COLOR_BLUE_MAIN, COLOR_FEMALE_PINK, GREEN_DARK, GREEN_LIGHT,
    COLOR_ONLINE, COLOR_INSTORE, AGE_GROUP_COLORS
)
from components.factories import component_factory as comp_factory
from components.factories.kpi_card_factory import create_kpi_card_body
from components.tabs.tab_home_components import (
    get_most_valuable_merchant_bar_chart, get_most_visited_merchants_bar_chart,
    get_spending_by_user_bar_chart, get_peak_hour_bar_chart, create_pie_graph,
    get_most_valuable_merchant_details, get_most_visited_merchant_details,
    get_top_spending_user_details, get_peak_hour_details, build_center_text,
    get_leader_info, get_age_leader_info
)
from frontend.icon_manager import IconID
from frontend.component_ids import ID
from frontend.layout.right.tabs.tab_home import BAR_CHART_OPTIONS

dm: DataManager = DataManager.get_instance()
home_data: HomeTabData = dm.home_tab_data

# Map of dropdown-values -> chart-builder functions
CHART_BUILDERS = {
    "most_valuable_merchants": get_most_valuable_merchant_bar_chart,
    "most_visited_merchants": get_most_visited_merchants_bar_chart,
    "top_spending_users": get_spending_by_user_bar_chart,
    "peak_hours": get_peak_hour_bar_chart,
}


@callback(
    Output(ID.HOME_GRAPH_BAR_CHART, "figure"),
    Input(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    Input(ID.HOME_TAB_BAR_CHART_DROPDOWN, "value"),
    Input(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "n_clicks"),
    Input(ID.APP_STATE_STORE, "data"),
    prevent_initial_call=True
)
def update_bar_chart(selected_state, chart_option, n_clicks_toggle, app_state):
    """
    Update the bar chart figure based on the selected state, chart option, button toggle, and application state.

    @parameters
    selected_state: str or None
        The state selected from the user interface. Used to filter the chart data. If None, all states should be included.
    chart_option: str or None
        The selected option from the dropdown to determine the type or configuration of the chart.
    n_clicks_toggle: int
        The number of times the toggle all states button has been clicked. Used to identify if the toggle button was triggered.
    app_state: dict or None
        A dictionary representing the application state. May contain settings like 'dark_mode' to customize the chart display.

    @raises
    PreventUpdate
        Raised when the chart_option is invalid or not found in the CHART_BUILDERS.

    @returns
    plotly.graph_objects.Figure
        The resulting figure for the bar chart after applying the selected filters and configurations.
    """
    trigger = ctx.triggered_id

    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        state = None
    else:
        state = selected_state

    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Validate chart_option
    builder = CHART_BUILDERS.get(chart_option)
    if builder is None:
        raise PreventUpdate

    return builder(state=state, dark_mode=dark_mode)


@callback(
    Output(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    Output(ID.MAP, "clickData"),
    Output(ID.KPI_CARD_AMT_TRANSACTIONS, "children"),
    Output(ID.KPI_CARD_SUM_OF_TRANSACTIONS, "children"),
    Output(ID.KPI_CARD_AVG_TRANSACTION_AMOUNT, "children"),
    Input(ID.MAP.value, "clickData"),
    Input(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "n_clicks"),
    prevent_initial_call=True
)
def store_selected_state(clickData, n_clicks):
    """
    Handles storing the selected state based on interaction with a map or toggle button. The function processes user
    interactions, such as clicking on a map location or a toggle button, and updates the state data accordingly.
    It also updates the KPI cards with state-specific data.

    Args:
        clickData: Dictionary containing data about a click event on the map. It includes details about the clicked
            location, such as coordinates or state identifier.
        n_clicks: Number of times the toggle button has been clicked.

    Returns:
        tuple: A tuple containing updated state data, clickData for the map, and updated KPI card contents.
            If the toggle button is clicked, state is set to None and KPIs show global data.
            If a map location is clicked, state data is updated with the clicked location, and KPIs show state-specific data.
    """
    # Get the context
    trigger = ctx.triggered_id

    # Set to none if button is clicked
    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        state = None
    # Save the state when clicked on the map
    elif clickData and clickData.get("points"):
        state = clickData["points"][0]["location"]
    else:
        # Otherwise do nothing
        raise PreventUpdate

    # Get KPI values for the selected state
    transaction_count, total_value, avg_value = home_data.get_state_kpi_values(state)

    # Get average KPI values per state for comparison
    avg_values = home_data.get_average_kpi_values_per_state()

    # Check if avg_values is None and provide default values if it is
    if avg_values is None:
        avg_transaction_count = transaction_count
        avg_total_value = total_value
        avg_transaction_value = avg_value
    else:
        avg_transaction_count, avg_total_value, avg_transaction_value = avg_values

    # Format KPI values for headers
    transaction_count_str = f"{transaction_count:,}".replace(",", ".")
    total_value_str = f"${total_value:,.2f}"
    avg_value_str = f"${avg_value:,.2f}"

    # Create KPI card headers
    kpi_transactions_header = dbc.CardHeader(

        children=[
            comp_factory.create_icon(IconID.CHART_PIPE, cls="icon icon-small"),
            html.Span(transaction_count_str, className="kpi-card-value kpi-number-value pt-1"),
            html.Span("Transactions", className="kpi-card-title")

        ]
    )

    kpi_total_value_header = dbc.CardHeader(
        children=[

            comp_factory.create_icon(IconID.MONEY_DOLLAR, cls="icon icon-small"),
            html.Span(total_value_str, className="kpi-card-value kpi-number-value pt-1"),
            html.Span("Total Value", className="kpi-card-title")

        ]
    )

    kpi_avg_value_header = dbc.CardHeader(
        children=[

            comp_factory.create_icon(IconID.CHART_AVERAGE, cls="icon icon-small"),
            html.Span(avg_value_str, className="kpi-card-value kpi-number-value pt-1"),
            html.Span("Avg. Transaction", className="kpi-card-title")

        ]
    )

    # Create KPI card bodies with comparison to average per state
    kpi_transactions_body = create_kpi_card_body(
        transaction_count,
        avg_transaction_count,
        lambda v: f"{v:,.2f}".replace(",", "."),
        state,
        ID.KPI_CARD_AMT_TRANSACTIONS_TOOLTIP
    )

    kpi_total_value_body = create_kpi_card_body(
        total_value, 
        avg_total_value, 
        lambda v: f"${v:,.2f}",
        state,
        ID.KPI_CARD_SUM_OF_TRANSACTIONS_TOOLTIP
    )

    kpi_avg_value_body = create_kpi_card_body(
        avg_value, 
        avg_transaction_value, 
        lambda v: f"${v:,.2f}",
        state,
        ID.KPI_CARD_AVG_TRANSACTION_AMOUNT_TOOLTIP
    )

    # Combine header and body for each KPI card
    kpi_transactions = [kpi_transactions_header, kpi_transactions_body]
    kpi_total_value = [kpi_total_value_header, kpi_total_value_body]
    kpi_avg_value = [kpi_avg_value_header, kpi_avg_value_body]

    # Return updated state, clickData, and KPI card contents
    return state, no_update if trigger != ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES else None, kpi_transactions, kpi_total_value, kpi_avg_value


@callback(
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_GENDER, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_AGE, "figure"),
    Output(ID.HOME_TAB_STATE_HEADING, "children"),
    Output(ID.HOME_KPI_MOST_VALUABLE_MERCHANT, "children"),
    Output(ID.HOME_KPI_MOST_VISITED_MERCHANT, "children"),
    Output(ID.HOME_KPI_TOP_SPENDING_USER, "children"),
    Output(ID.HOME_KPI_PEAK_HOUR, "children"),
    Output(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "className"),
    Input(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "n_clicks"),
    Input(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    Input(ID.APP_STATE_STORE, "data"),
    prevent_initial_call=True
)
def update_all_pies(n_clicks_toggle, selected_state, app_state):
    """
    Updates multiple pie charts, headings, KPIs, and button classes based on user interaction and state selection.

    This callback is responsible for updating the gender, channel, and age-based expenditure pie charts,
    updating the state-specific heading text, recalculating various Key Performance Indicators (KPIs),
    and modifying the visibility/classes of UI elements. The updates dynamically adapt based on the user's
    input actions such as toggling between all states and specific state selections or enabling/disabling
    dark mode.

    Args:
        n_clicks_toggle (int): The number of times the "Toggle All States" button is clicked. Used to
            switch between all states and a specific state view.
        n_clicks_dark (int): The number of times the dark mode toggle button is clicked. Used to enable
            or disable dark mode based on the parity of the number of clicks.
        selected_state (str): The currently selected state, represented as a string. It determines
            the scope of data visualizations (e.g., Gender, Channel, and Age expenditures) and KPIs.
        app_state: The current application state containing settings like dark_mode.

    Returns:
        tuple: A tuple containing the following elements:
            - (plotly.graph_objects.Figure) The updated pie chart for expenditures by gender.
            - (plotly.graph_objects.Figure) The updated pie chart for expenditures by channel.
            - (plotly.graph_objects.Figure) The updated pie chart for expenditures by age.
            - (str) The updated heading for the state or "All States".
            - (str) The name/details of the most valuable merchant based on the selected state.
            - (str) The name/details of the most visited merchant based on the selected state.
            - (str) The name/details of the top spending user based on the selected state.
            - (str) The peak hour details indicating the time of highest expenditures.
            - (str) The CSS class name for the toggle button, indicating its visibility or styling.
    """
    # Context, State, Dark Mode
    trigger = ctx.triggered_id
    state = None if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES else selected_state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE
    color_green = GREEN_DARK if dark_mode else GREEN_LIGHT

    # Gender
    gender_sums = home_data.get_expenditures_by_gender(state=state).copy()
    gender_label_colors = {"MALE": COLOR_BLUE_MAIN, "FEMALE": COLOR_FEMALE_PINK}
    labels_gender = list(gender_sums.keys())
    colors_gender = [gender_label_colors.get(label, "#cccccc") for label in labels_gender]
    gender_leader, leader_color, diff = get_leader_info(gender_sums, gender_label_colors)
    center_text_gender = build_center_text(gender_leader, leader_color, diff, color_green,
                                           font_size=17, value_font_size=12)

    hover_template_gender = (
        "🧑‍🤝‍🧑 <b>GENDER:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_gender = create_pie_graph(
        data=gender_sums, dark_mode=dark_mode, showlegend=False,
        hover_template=hover_template_gender, center_text=center_text_gender,
        colors=colors_gender
    )

    # Channel
    channel_sums = home_data.get_expenditures_by_channel(state=state)
    channel_label_colors = {"ONLINE": COLOR_ONLINE, "IN-STORE": COLOR_INSTORE}
    channel_leader, leader_color, diff = get_leader_info(channel_sums, channel_label_colors)
    center_text_channel = build_center_text(channel_leader, leader_color, diff, color_green, tie_label="TIE",
                                            font_size=15, value_font_size=12)

    hover_template_channel = (
        "🛒‍ <b>CHANNEL:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_channel = create_pie_graph(
        data=channel_sums, dark_mode=dark_mode, showlegend=False,
        colors=[COLOR_ONLINE, COLOR_INSTORE], hover_template=hover_template_channel,
        center_text=center_text_channel
    )

    # Age
    age_sums = home_data.get_expenditures_by_age(state=state)
    top_group, color_leader, top_value, percent, total = get_age_leader_info(age_sums, AGE_GROUP_COLORS)
    center_text_age = build_center_text(top_group, color_leader, None, color_green, tie_label="NO DATA",
                                        value=top_value, percent=None,
                                        font_size=17, value_font_size=12)

    hover_template_age = (
        "🎂 <b>AGE:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_age = create_pie_graph(
        data=age_sums, dark_mode=dark_mode, showlegend=False,
        textinfo="label", hover_template=hover_template_age,
        center_text=center_text_age, colors=AGE_GROUP_COLORS
    )

    # Heading & KPIs & Buttons
    heading = (
        "All States" if state is None
        else "ONLINE" if state == "ONLINE"
        else f"State: {state}"
    )
    kpi1 = get_most_valuable_merchant_details(state=state)
    kpi2 = get_most_visited_merchant_details(state=state)
    kpi3 = get_top_spending_user_details(state=state)
    kpi4 = get_peak_hour_details(state=state)
    base_cls = "settings-button-text map-toggle-states-button"
    button_cls = base_cls if state is not None else f"{base_cls} hidden"

    return (
        fig_gender, fig_channel, fig_age, heading, kpi1, kpi2, kpi3, kpi4, button_cls
    )


@callback(
    Output(ID.USER_ID_SEARCH_INPUT, "value"),  # User Tab -> Input -> Search by User ID
    Output(ID.MERCHANT_INPUT_MERCHANT_ID, "value", allow_duplicate=True),
    # Merchant Tab -> Input -> Search by Merchant ID
    Output(ID.ACTIVE_TAB_STORE, "data", allow_duplicate=True),  # Active Tab Store
    Output(ID.HOME_GRAPH_BAR_CHART, "clickData"),  # Home Graph Bar Chart
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data", allow_duplicate=True),  # Merchant Button Store
    Input(ID.HOME_GRAPH_BAR_CHART, "clickData"),
    State(ID.HOME_TAB_BAR_CHART_DROPDOWN, "value"),
    prevent_initial_call=True
)
def bridge_home_to_user_tab(click_data, chart_option):
    """
    Updates the user input and active tab based on interactions with the bar chart
    in the home tab. This callback bridges data between the home tab and
    the user tab for smoother navigation and display updates.

    Parameters:
        click_data: dict
            The data from the click event on the bar chart in the home tab.
            It contains details about the clicked bar such as x and y coordinates.
        chart_option: str
            The selected chart option from the dropdown in the home tab.

    Returns:
        tuple
            A tuple containing the new value for the user ID search input and
            the identifier of the active tab. If no update is necessary
            for either, the no_update constant is returned to preserve the current state.

    Raises:
        PreventUpdate
            Raised when no click event data is available, interrupting updates
            to prevent unnecessary computations and state changes.
    """
    if click_data is None:
        raise PreventUpdate

    # Top Spending User --> User Tab
    if chart_option == BAR_CHART_OPTIONS[2]["value"]:
        return click_data["points"][0]["x"], no_update, ID.TAB_USER, None, no_update

    # Most Valuable / Visited Merchant --> Merchant Tab
    elif chart_option == BAR_CHART_OPTIONS[0]["value"] or chart_option == BAR_CHART_OPTIONS[1]["value"]:
        return no_update, click_data["points"][0]["x"], ID.TAB_MERCHANT, None, ID_TO_MERCHANT_TAB.get(
            ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT).value

    # TODO: Add other chart options here if needed

    return no_update, no_update, no_update, no_update, no_update
