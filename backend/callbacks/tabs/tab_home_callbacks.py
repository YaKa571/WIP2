from dash import callback, Output, Input, ctx, no_update, State
from dash.exceptions import PreventUpdate

from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_home_data_setup import get_most_valuable_merchant_bar_chart, \
    get_most_visited_merchants_bar_chart, get_spending_by_user_bar_chart, get_peak_hour_bar_chart, create_pie_graph, \
    get_most_valuable_merchant_details, get_most_visited_merchant_details, get_top_spending_user_details, \
    get_peak_hour_details
from components.rightcolumn.tabs.tab_home import BAR_CHART_OPTIONS
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()

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
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
    prevent_initial_call=True
)
def update_bar_chart(selected_state, chart_option, n_clicks_toggle, n_clicks_dark):
    trigger = ctx.triggered_id

    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        state = None
    else:
        state = selected_state

    # Determine dark mode
    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    # Validate chart_option
    builder = CHART_BUILDERS.get(chart_option)
    if builder is None:
        raise PreventUpdate

    fig = builder(state=state, dark_mode=dark_mode)
    return fig


@callback(
    Output(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    Output(ID.MAP, "clickData"),
    Input(ID.MAP.value, "clickData"),
    Input(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "n_clicks"),
    prevent_initial_call=True
)
def store_selected_state(clickData, n_clicks):
    # Get the context
    trigger = ctx.triggered_id

    # Set to none if button is clicked
    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        return None, None

    # Save the state when clicked on the map
    if clickData and clickData.get("points"):
        state = clickData["points"][0]["location"]
        return state, no_update

    # Otherwise do nothing
    raise PreventUpdate


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
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
    Input(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    prevent_initial_call=True
)
def update_all_pies(n_clicks_toggle, n_clicks_dark, selected_state):
    """
    Updates multiple pie chart figures, heading text, KPI details, and the class name of a toggle button
    based on the user's interactions and selected state. Handles dark mode toggling and state selection
    to update visual components and textual details dynamically based on the application's data.

    Args:
        n_clicks_toggle (int | None): Number of times the "Toggle All States" button has been clicked.
        n_clicks_dark (int | None): Number of times the dark mode toggle button has been clicked.
        selected_state (str | None): The state currently selected in the application, or None if in all-state mode.

    Returns:
        tuple: A tuple containing updated properties for the application interface:
            - Figure for expenditures by gender.
            - Figure for expenditures by channel.
            - Figure for expenditures by age.
            - Heading text displaying the current state being analyzed.
            - Most valuable merchant as a KPI detail.
            - Most visited merchant as a KPI detail.
            - Top spending user as a KPI detail.
            - Peak hour as a KPI detail.
            - Updated class name for the "Toggle All States" button.
    """
    # Get the context
    trigger = ctx.triggered_id

    # Determine the current state
    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        state = None
    else:
        state = selected_state

    # Determine dark mode
    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    # Aggregate data (cached getters)
    gender_sums = dm.get_expenditures_by_gender(state=state).copy()
    channel_sums = dm.get_expenditures_by_channel(state=state)
    age_sums = dm.get_expenditures_by_age(state=state)

    # Build figures

    hover_template_gender = (
        "🧑‍🤝‍🧑 <b>GENDER:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_gender = create_pie_graph(data=gender_sums, dark_mode=dark_mode, showlegend=False,
                                  hover_template=hover_template_gender)

    hover_template_channel = (
        "🛒‍ <b>CHANNEL:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_channel = create_pie_graph(data=channel_sums, dark_mode=dark_mode, showlegend=False,
                                   colors=["#FFCD00", "#81C784"], hover_template=hover_template_channel)

    hover_template_age = (
        "🎂 <b>AGE:</b> %{label}<br>"
        "📊 <b>SHARE:</b> %{percent}<br>"
        "💰 <b>SUM:</b> $%{value:,.2f}"
    )

    fig_age = create_pie_graph(data=age_sums, dark_mode=dark_mode, showlegend=False,
                               textinfo="label", hover_template=hover_template_age)

    # Heading and KPI details
    heading = "All States" if state is None else f"State: {state}"
    kpi1 = get_most_valuable_merchant_details(state=state)
    kpi2 = get_most_visited_merchant_details(state=state)
    kpi3 = get_top_spending_user_details(state=state)
    kpi4 = get_peak_hour_details(state=state)

    # Only show the button when a state is selected
    base_cls = "settings-button-text"
    button_cls = base_cls if state is not None else f"{base_cls} hidden"

    return (
        fig_gender,
        fig_channel,
        fig_age,
        heading,
        kpi1,
        kpi2,
        kpi3,
        kpi4,
        button_cls
    )


@callback(
    Output(ID.USER_ID_SEARCH_INPUT, "value"),
    Output(ID.ACTIVE_TAB_STORE, "data"),
    Output(ID.HOME_GRAPH_BAR_CHART, "clickData"),
    Input(ID.HOME_GRAPH_BAR_CHART, "clickData"),
    State(ID.HOME_TAB_BAR_CHART_DROPDOWN, "value"),
    prevent_initial_call=True
)
def bridge_home_to_user_tab(clickData, chart_option):
    """
    Updates the user input and active tab based on interactions with the bar chart
    in the home tab. This callback bridges data between the home tab and
    the user tab for smoother navigation and display updates.

    Parameters:
        clickData: dict
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
    if clickData is None:
        raise PreventUpdate

    # Top Spending User -> User Tab
    if chart_option == BAR_CHART_OPTIONS[2]["value"]:
        return clickData["points"][0]["x"], ID.TAB_USER, None

    # TODO: Add other chart options here if needed

    return no_update, no_update, no_update
