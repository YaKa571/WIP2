from dash import callback, Output, Input, ctx, no_update
from dash.exceptions import PreventUpdate

from backend.data_manager import DataManager
from components.rightcolumn.tabs.tab_home import create_pie_graph, get_most_valuable_merchant_details, \
    get_most_visited_merchant_details, get_top_spending_user_details, get_peak_hour_details
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()


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
    gender_sums = dm.get_expenditures_by_gender(state=state)
    channel_sums = dm.get_expenditures_by_channel(state=state)
    age_sums = dm.get_expenditures_by_age(state=state)

    # Build figures
    fig_gender = create_pie_graph(data=gender_sums, dark_mode=dark_mode, showlegend=False)
    fig_channel = create_pie_graph(data=channel_sums, dark_mode=dark_mode, showlegend=False,
                                   colors=["#FFCD00", "#81C784"])
    fig_age = create_pie_graph(data=age_sums, dark_mode=dark_mode, showlegend=False,
                               textinfo="label")

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
