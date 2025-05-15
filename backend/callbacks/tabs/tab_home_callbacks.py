from dash import callback, Output, Input, ctx
from dash.exceptions import PreventUpdate

from backend.data_manager import DataManager
from components.rightcolumn.tabs.tab_home import create_pie_graph, get_most_valuable_merchant_details, \
    get_most_visited_merchant_details, get_top_spending_user_details, get_peak_hour_details
from frontend.component_ids import ID

dm: DataManager = DataManager.get_instance()


@callback(
    Output(ID.HOME_TAB_SELECTED_STATE_STORE, "data"),
    Input(ID.MAP.value, "clickData"),
    prevent_initial_call=True
)
def store_selected_state(clickData):
    # If no clickData, do nothing
    if not clickData or not clickData.get("points"):
        raise PreventUpdate
    # Extract state name from clicked point
    return clickData["points"][0]["location"]


@callback(
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_GENDER, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL, "figure"),
    Output(ID.HOME_GRAPH_EXPENDITURES_BY_AGE, "figure"),
    Output(ID.HOME_TAB_STATE_HEADING, "children"),
    Output(ID.HOME_KPI_MOST_VALUABLE_MERCHANT, "children"),
    Output(ID.HOME_KPI_MOST_VISITED_MERCHANT, "children"),
    Output(ID.HOME_KPI_TOP_SPENDING_USER, "children"),
    Output(ID.HOME_KPI_PEAK_HOUR, "children"),
    Input(ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES, "n_clicks"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
    Input(ID.HOME_TAB_SELECTED_STATE_STORE, "data")
)
def update_all_pies(_, n_clicks, selected_state):
    # Determine dark mode from the store
    dark_mode = bool(n_clicks and n_clicks % 2 == 1)

    # Figure out which input triggered the callback
    trigger = ctx.triggered_id

    # If the "Show all States" button was clicked, override state to None
    if trigger == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES:
        state = None
    else:
        state = selected_state

    # Fetch filtered aggregations
    gender_sums = dm.get_expenditures_by_gender(state=state)
    channel_sums = dm.get_expenditures_by_channel(state=state)
    age_sums = dm.get_expenditures_by_age(state=state)

    # Build figures
    fig_gender = create_pie_graph(
        data=gender_sums,
        dark_mode=dark_mode,
        showlegend=False
    )

    fig_channel = create_pie_graph(
        data=channel_sums,
        dark_mode=dark_mode,
        showlegend=False,
        colors=["#FFCD00", "#81C784"]
    )

    fig_age = create_pie_graph(
        data=age_sums,
        dark_mode=dark_mode,
        showlegend=False,
        textinfo="label"
    )

    return (
        fig_gender,
        fig_channel,
        fig_age,
        f"State: {state}" if state else "All States",
        get_most_valuable_merchant_details(state=state),
        get_most_visited_merchant_details(state=state),
        get_top_spending_user_details(state=state),
        get_peak_hour_details(state=state)
    )
