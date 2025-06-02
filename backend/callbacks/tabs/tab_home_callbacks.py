from dash import callback, Output, Input, ctx, no_update, State
from dash.exceptions import PreventUpdate

import components.constants as const
from backend.callbacks.tabs.tab_merchant_callbacks import ID_TO_MERCHANT_TAB
from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_home_data import HomeTabData
from components.constants import (
    COLOR_BLUE_MAIN, COLOR_FEMALE_PINK, GREEN_DARK, GREEN_LIGHT,
    COLOR_ONLINE, COLOR_INSTORE, AGE_GROUP_COLORS
)
from components.tabs.tab_home_components import (
    get_most_valuable_merchant_bar_chart, get_most_visited_merchants_bar_chart,
    get_spending_by_user_bar_chart, get_peak_hour_bar_chart, create_pie_graph,
    get_most_valuable_merchant_details, get_most_visited_merchant_details,
    get_top_spending_user_details, get_peak_hour_details, build_center_text,
    get_leader_info, get_age_leader_info
)
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
    Updates the bar chart figure based on the selected state, chart options, and user interaction.

    This callback function dynamically generates a bar chart figure for display.
    It re-renders the figure when any of its inputs change, including the selected
    state, chart type option, or toggle actions for all states and dark mode. The
    function also provides support for toggling dark mode UI representation.

    Args:
        selected_state: Data representing the current state selection.
        chart_option: Selected option for bar chart type.
        n_clicks_toggle: Number of clicks on the "Toggle All States" button.
        n_clicks_dark: Number of clicks on the "Dark Mode Toggle" button.
        app_state: The current application state containing settings like dark_mode.

    Returns:
        A plotly figure object for the updated bar chart.
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
    """
    Handles storing the selected state based on interaction with a map or toggle button. The function processes user
    interactions, such as clicking on a map location or a toggle button, and updates the state data accordingly.

    Args:
        clickData: Dictionary containing data about a click event on the map. It includes details about the clicked
            location, such as coordinates or state identifier.
        n_clicks: Number of times the toggle button has been clicked.

    Returns:
        tuple: A tuple containing updated state data and clickData for the map. The returned values depend on the user
            interaction that triggered the callback. If the toggle button is clicked, both values are set to None. If a map
            location is clicked, state data is updated with the clicked location, and the map clickData remains unchanged.
    """
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
    base_cls = "settings-button-text"
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

    # Top Spending User -> User Tab
    if chart_option == BAR_CHART_OPTIONS[2]["value"]:
        return click_data["points"][0]["x"], no_update, ID.TAB_USER, None, no_update

    # Most Valuable / Visited Merchant --> Merchant Tab
    elif chart_option == BAR_CHART_OPTIONS[0]["value"] or chart_option == BAR_CHART_OPTIONS[1]["value"]:
        return no_update, click_data["points"][0]["x"], ID.TAB_MERCHANT, None, ID_TO_MERCHANT_TAB.get(
            ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT).value

    # TODO: Add other chart options here if needed

    return no_update, no_update, no_update, no_update, no_update
