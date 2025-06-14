from enum import Enum

from dash import dcc, html, callback, Input, Output, ctx, State

import components.constants as const
import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from components.tabs.tab_cluster_components import make_cluster_plot, create_cluster_legend, make_inc_vs_exp_plot
from frontend.component_ids import ID

# Initialize DataManager instance
dm: DataManager = DataManager.get_instance()
cluster_data = dm.cluster_tab_data


class ClusterMainOption(str, Enum):
    TOTAL_VALUE = "total_value"
    AVERAGE_VALUE = "average_value"
    INC_VS_EXP = "inc_vs_exp"


class ClusterAgeOption(str, Enum):
    ALL_AGES = "all_ages"
    AGE_GROUPS = "age_groups"


ID_TO_MAIN_OPTION = {
    ID.CLUSTER_BTN_TOTAL_VALUE: ClusterMainOption.TOTAL_VALUE,
    ID.CLUSTER_BTN_AVERAGE_VALUE: ClusterMainOption.AVERAGE_VALUE,
    ID.CLUSTER_BTN_INC_VS_EXP: ClusterMainOption.INC_VS_EXP,
}

ID_TO_AGE_OPTION = {
    ID.CLUSTER_BTN_ALL_AGES: ClusterAgeOption.ALL_AGES,
    ID.CLUSTER_BTN_AGE_GROUP: ClusterAgeOption.AGE_GROUPS,
}

OPTION_BUTTON_BASE_CLASS = "settings-button-text option-btn"


def get_option_button_class(option: str, selected_option: str) -> str:
    """
    Determines the CSS class for an option button based on its selection status.

    This function evaluates whether the specified option matches the currently
    selected option and assigns the appropriate CSS class to the button.

    Args:
        option (str): The option to evaluate.
        selected_option (str): The currently selected option.

    Returns:
        str: The CSS class for the option button.
    """
    return (
        f"{OPTION_BUTTON_BASE_CLASS} selected active-button"
        if selected_option == option else
        OPTION_BUTTON_BASE_CLASS
    )


@callback(
    Output(ID.CLUSTER_SELECTED_BUTTON_STORE, "data"),
    Input(ID.CLUSTER_BTN_TOTAL_VALUE, 'n_clicks'),
    Input(ID.CLUSTER_BTN_AVERAGE_VALUE, 'n_clicks'),
    Input(ID.CLUSTER_BTN_INC_VS_EXP, 'n_clicks'),
    Input(ID.CLUSTER_BTN_ALL_AGES, 'n_clicks'),
    Input(ID.CLUSTER_BTN_AGE_GROUP, 'n_clicks'),
    State(ID.CLUSTER_SELECTED_BUTTON_STORE, "data"),
    prevent_initial_call=True,
)
def set_cluster_tab(n_total_value, n_average_value, n_inc_vs_exp, n_all_ages, n_age_groups, store_data):
    """
    Callback function to update the cluster tab store data based on user interactions with cluster-related buttons.
    The function responds to buttons for total value, average value, income vs expense,
    all ages, and age groups, updating the corresponding stored data based on the input triggered.

    Parameters:
        n_total_value: int
            Number of clicks for the button related to "total value".
        n_average_value: int
            Number of clicks for the button related to "average value".
        n_inc_vs_exp: int
            Number of clicks for the button related to "income vs expense".
        n_all_ages: int
            Number of clicks for the button related to "all ages".
        n_age_groups: int
            Number of clicks for the button related to "age groups".
        store_data: dict
            The current store data that maintains the selected cluster states.

    Returns:
        dict
            Updated store data reflecting the selected cluster option based on the triggered input.
    """
    trigger_id = ctx.triggered_id
    new_store = store_data.copy()

    # Main options
    if trigger_id in ID_TO_MAIN_OPTION:
        new_store["main"] = ID_TO_MAIN_OPTION[trigger_id].value

    # Age options
    elif trigger_id in ID_TO_AGE_OPTION:
        new_store["age"] = ID_TO_AGE_OPTION[trigger_id].value
    return new_store


@callback(
    Output(ID.CLUSTER_BTN_TOTAL_VALUE, "className"),
    Output(ID.CLUSTER_BTN_AVERAGE_VALUE, "className"),
    Output(ID.CLUSTER_BTN_INC_VS_EXP, "className"),
    Output(ID.CLUSTER_BTN_ALL_AGES, "className"),
    Output(ID.CLUSTER_BTN_AGE_GROUP, "className"),
    Output(ID.CLUSTER_GRAPH, "figure"),
    Output(ID.CLUSTER_LEGEND, "children"),
    Output(ID.CLUSTER_HEADING, "children"),
    Input(ID.CLUSTER_SELECTED_BUTTON_STORE, "data"),
    Input(ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN, "value"),
    Input(ID.APP_STATE_STORE, "data"),
    Input(ID.HOME_TAB_SELECTED_STATE_STORE,"data"),
)
def update_cluster(selected, selected_merchant_group, app_state, selected_federal_state):
    """
    Updates the cluster-related components, such as buttons, graph, legend, and the heading,
    based on user interaction and selected input data. Determines which cluster data to display
    (total value, average value, or income vs expenditure) and whether this data should be grouped
    by age. Applies a dark mode theme if necessary and adjusts the federal state selection.

    Args:
        selected (dict): Data representing the currently selected options for main
            cluster criteria and age grouping.
        selected_merchant_group (str): Group of merchants selected for filtering the data.
        app_state (dict): Dictionary containing application state data such as
            whether dark mode is enabled.
        selected_federal_state (str): Selected federal state identifier, used to filter
            data to a specific state or to represent all states.

    Returns:
        tuple: A tuple containing the following outputs:
            - str: CSS class for the 'Total Value' button.
            - str: CSS class for the 'Average Value' button.
            - str: CSS class for the 'Income vs Expenditure' button.
            - str: CSS class for the 'All Ages' button.
            - str: CSS class for the 'Age Group' button.
            - plotly.graph_objs.Figure: Figure object for cluster visualization.
            - dash.development.base_component.Component: Legend component for cluster visualization.
            - str: Heading text for the cluster section.
    """
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # federal state
    federal_state = None if ctx.triggered_id == ID.HOME_TAB_BUTTON_TOGGLE_ALL_STATES else selected_federal_state
    heading = (
        "All States" if federal_state is None
        else "ONLINE" if federal_state == "ONLINE"
        else f"State: {federal_state}"
    )

    if not selected:
        selected = {
            "main": ClusterMainOption.TOTAL_VALUE.value,
            "age": ClusterAgeOption.ALL_AGES.value
        }

    selected_main = selected["main"]
    selected_age = selected["age"]

    if selected_main == ClusterMainOption.TOTAL_VALUE.value and selected_age == ClusterAgeOption.ALL_AGES.value:
        df_clustered = cluster_data.prepare_cluster_data(selected_merchant_group, federal_state)
        fig = make_cluster_plot(df_clustered, mode="total_value", age_group_mode="not grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="total_value", df=df_clustered)

    elif selected_main == ClusterMainOption.TOTAL_VALUE.value and selected_age == ClusterAgeOption.AGE_GROUPS.value:
        df_clustered = cluster_data.prepare_cluster_data(selected_merchant_group, federal_state)
        fig = make_cluster_plot(df_clustered, mode="total_value", age_group_mode="grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="total_value", df=df_clustered)

    elif selected_main == ClusterMainOption.AVERAGE_VALUE.value and selected_age == ClusterAgeOption.ALL_AGES.value:
        df_clustered = cluster_data.prepare_cluster_data(selected_merchant_group, federal_state)
        fig = make_cluster_plot(df_clustered, mode="average_value", age_group_mode="not grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="average_value", df=df_clustered)

    elif selected_main == ClusterMainOption.AVERAGE_VALUE.value and selected_age == ClusterAgeOption.AGE_GROUPS.value:
        df_clustered = cluster_data.prepare_cluster_data(selected_merchant_group, federal_state)
        fig = make_cluster_plot(df_clustered, mode="average_value", age_group_mode="grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="average_value", df=df_clustered)

    elif selected_main == ClusterMainOption.INC_VS_EXP.value and selected_age == ClusterAgeOption.ALL_AGES.value:
        df_clustered = cluster_data.prepare_inc_vs_exp_cluster_data(selected_merchant_group)
        fig = make_inc_vs_exp_plot(df_clustered, age_group_mode="not grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="inc_vs_exp", df=df_clustered)

    elif selected_main == ClusterMainOption.INC_VS_EXP.value and selected_age == ClusterAgeOption.AGE_GROUPS.value:
        df_clustered = cluster_data.prepare_inc_vs_exp_cluster_data(selected_merchant_group)
        fig = make_inc_vs_exp_plot(df_clustered, age_group_mode="grouped", dark_mode=dark_mode)
        legend = create_cluster_legend(mode="inc_vs_exp", df=df_clustered)

    else:
        fig = comp_factory.create_empty_figure()
        legend = html.Div([html.P("No Legend")])

    return (
        get_option_button_class(ClusterMainOption.TOTAL_VALUE.value, selected_main),
        get_option_button_class(ClusterMainOption.AVERAGE_VALUE.value, selected_main),
        get_option_button_class(ClusterMainOption.INC_VS_EXP.value, selected_main),
        get_option_button_class(ClusterAgeOption.ALL_AGES.value, selected_age),
        get_option_button_class(ClusterAgeOption.AGE_GROUPS.value, selected_age),
        fig,
        legend,
        heading
    )


def get_cluster_merchant_group_input() -> dcc.Dropdown:
    """
    Returns a dropdown component for selecting a merchant group within a cluster-based
    data setup.

    This function fetches merchant groups from an external data source, formats them
    into dropdown options, and creates a pre-populated dropdown for the user's selection.

    Returns
    -------
    dcc.Dropdown
        A Dash dropdown component pre-configured with merchant group options, a default
        selection if available, or a placeholder if no groups exist. The dropdown is
        searchable, not clearable, and supports single selection only.
    """
    merchant_groups = cluster_data.get_cluster_merchant_group_dropdown()
    options = [{'label': group, 'value': group} for group in merchant_groups]

    default_value = merchant_groups[0] if merchant_groups else None

    return dcc.Dropdown(
        id=ID.CLUSTER_MERCHANT_INPUT_GROUP_DROPDOWN,
        className="settings-dropdown settings-text-centered",
        options=options,
        value=default_value,
        placeholder="Choose a Merchant Group...",
        searchable=True,
        clearable=False,
        multi=False,
        style={"width": "100%"}
    )


@callback(
    Output(ID.CLUSTER_COLLAPSE_LEGEND, "is_open"),
    Output(ID.CLUSTER_BTN_TOGGLE_LEGEND, "children"),
    Input(ID.CLUSTER_BTN_TOGGLE_LEGEND, "n_clicks"),
    State(ID.CLUSTER_COLLAPSE_LEGEND, "is_open"),
    prevent_initial_call=True
)
def toggle_legend(n_clicks, is_open):
    """
    Toggle the visibility of a legend section and update the icon displayed on a button.

    Toggles the "is_open" state of a legend section and modifies the button's icon based
    on the toggled state. This function is triggered by button clicks.

    @param n_clicks: The number of times the button has been clicked.
        A positive integer indicating the number of button clicks.
    @param is_open: Indicates whether the legend section is currently open.
        A boolean value where True represents that the legend is open,
        and False indicates it is closed.

    @return:
        A tuple containing:
        - The new state for the "is_open" property of the legend section,
          where True means the legend section is closed and False means it is open.
        - The icon element (html.I) that should be displayed on the button,
          either an up arrow or a down arrow.
    """
    new_state = not is_open
    icon = html.I(className="fa fa-chevron-up") if new_state else html.I(className="fa fa-chevron-down")

    return new_state, icon
