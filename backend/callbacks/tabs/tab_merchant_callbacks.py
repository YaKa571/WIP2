from enum import Enum

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, Output, Input, callback, ctx, State, callback_context, no_update

import components.constants as const
from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from components.tabs.tab_merchant_components import create_merchant_group_line_chart, \
    create_individual_merchant_line_chart
from frontend.component_ids import ID
from frontend.icon_manager import IconID
from backend.data_handler import merchant_other_threshold

# Initialize DataManager instance
dm: DataManager = DataManager.get_instance()

"""
Callbacks and factories for tab Merchant.
"""


class MerchantTab(str, Enum):
    ALL = "all"
    GROUP = "group"
    INDIVIDUAL = "individual"


ID_TO_MERCHANT_TAB = {
    ID.MERCHANT_BTN_ALL_MERCHANTS: MerchantTab.ALL,
    ID.MERCHANT_BTN_MERCHANT_GROUP: MerchantTab.GROUP,
    ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT: MerchantTab.INDIVIDUAL,
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


# === KPI Card Factory ===

def create_kpi_card(icon, title, value_1, value_2, value_id, value_1_class="", value_2_class=""):
    return html.Div(  # <- jetzt klickbar
        id=value_id,
        n_clicks=0,
        style={"cursor": "pointer"},
        children=[
            dbc.Card(
                className="card kpi-card",
                children=[
                    dbc.CardHeader(
                        className="card-header",
                        children=[
                            comp_factory.create_icon(icon, cls="icon icon-small"),
                            html.P(title, className="kpi-card-title"),
                        ]
                    ),
                    dbc.CardBody(
                        className="card-body",
                        children=[
                            html.Div(
                                children=[
                                    html.P(value_1, className=f"kpi-card-value {value_1_class}"),
                                    html.P(value_2, className=f"kpi-card-value kpi-number-value {value_2_class}"),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_kpi_dashboard(kpi_data):
    """
    Creates a KPI dashboard as a flexible wrapper containing KPI cards.

    This function takes a list of KPI data dictionaries, creates individual KPI
    cards using the provided data, and returns a wrapper component containing
    all these KPI cards.

    Args:
        kpi_data: list
            A list of dictionaries, where each dictionary contains data
            required to create a KPI card.

    Returns:
        dash.html.Div
            A Div component acting as a wrapper that includes all created KPI
            cards.
    """
    return html.Div(
        className="flex-wrapper",
        children=[create_kpi_card(**kpi) for kpi in kpi_data]
    )


def create_all_merchant_kpis():
    """
    Generates and compiles a list of merchant-related key performance indicators (KPIs) and returns a KPI dashboard.

    The function utilizes data from merchant groups and user transactions to calculate four KPIs: the most frequently
    used merchant group, the merchant group with the highest transfer value, the user with the most transactions across
    all merchants, and the user with the highest expenditure. Each KPI is structured and styled with corresponding icons,
    titles, and values before being compiled into a dashboard format.

    Returns:
        Dashboard: A dashboard object containing the calculated merchant KPIs.

    """
    group_1, count_1 = dm.merchant_tab_data.get_most_frequently_used_merchant_group()
    group_2, value_2 = dm.merchant_tab_data.get_highest_value_merchant_group()
    user_3, count_3 = dm.merchant_tab_data.get_user_with_most_transactions_all_merchants()
    user_4, value_4 = dm.merchant_tab_data.get_user_with_highest_expenditure_all_merchants()

    kpi_data = [
        {
            "icon": IconID.CHART_PIPE,
            "title": "Top Merchant Group (by Transactions)",
            "value_1": group_1,
            "value_2": f"{count_1:,} Transactions",
            "value_id": ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP
        },
        {
            "icon": IconID.MONEY_DOLLAR,
            "title": "Top Merchant Group (by Value)",
            "value_1": group_2,
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP
        },
        {
            "icon": IconID.TRANSACTION_BY_CARD,
            "title": "Top User (by Transactions)",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3:,} Transactions",
            "value_id": ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL
        },
        {
            "icon": IconID.MONEY_WINGS,
            "title": "Top User (by Expenditure)",
            "value_1": f"ID {user_4}",
            "value_2": f"${value_4:,.2f}",
            "value_id": ID.MERCHANT_KPI_USER_HIGHEST_VALUE_ALL
        },
    ]
    return create_kpi_dashboard(kpi_data)


def create_merchant_group_kpi(merchant_group):
    """
    Generates KPI data for a given merchant group and creates a KPI dashboard.

    This function calculates various key performance indicators (KPIs) for a
    specified merchant group. It does so by identifying metrics such as the
    most frequently used merchant, the merchant with the highest total
    transactions, the user with the most transactions, and the user with the
    highest expenditure in the merchant group. These metrics are then used to
    construct a structured KPI data set, which is passed to a helper function
    to generate a KPI dashboard.

    Args:
        merchant_group: The group of merchants for which the KPI data is to be
            generated.

    Returns:
        A dashboard object created from the generated KPI data.
    """
    merchant_1, count_1 = dm.merchant_tab_data.get_most_frequently_used_merchant_in_group(merchant_group)
    merchant_2, value_2 = dm.merchant_tab_data.get_highest_value_merchant_in_group(merchant_group)
    user_3, count_3 = dm.merchant_tab_data.get_user_with_most_transactions_in_group(merchant_group)
    user_4, value_4 = dm.merchant_tab_data.get_user_with_highest_expenditure_in_group(merchant_group)

    kpi_data = [
        {
            "icon": IconID.CHART_PIPE,
            "title": "Top Merchant (by Transactions)",
            "value_1": f"ID {merchant_1}",
            "value_2": f"{count_1:,} Transactions",
            "value_id": ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP
        },
        {
            "icon": IconID.MONEY_DOLLAR,
            "title": "Top Merchant (by Value)",
            "value_1": f"ID {merchant_2}",
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP
        },
        {
            "icon": IconID.TRANSACTION_BY_CARD,
            "title": "Top User (by Transactions)",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3:,} Transactions",
            "value_id": ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP
        },
        {
            "icon": IconID.MONEY_WINGS,
            "title": "Top User (by Expenditure)",
            "value_1": f"ID {user_4}",
            "value_2": f"${value_4:,.2f}",
            "value_id": ID.MERCHANT_KPI_USER_HIGHEST_VALUE_IN_GROUP
        },
    ]
    return create_kpi_dashboard(kpi_data)


def create_individual_merchant_kpi(merchant: int = None):
    """
    Generate individual Key Performance Indicators (KPIs) for a merchant by collecting relevant transaction and
    user data.

    Args:
        merchant (int, optional): A unique identifier for the merchant whose KPIs are to be generated.
                                 If None, all values will display "NO DATA". Defaults to None.

    Returns:
        dict: A dashboard representation of the merchant's KPIs, formatted for display.

    Raises:
        None
    """
    if merchant is None:
        # If merchant is None, set all values to "WAITING FOR INPUT..."
        kpi_data = [
            {
                "icon": IconID.CHART_PIPE,
                "title": "Transactions",
                "value_1": "",
                "value_2": "WAITING FOR INPUT...",
                "value_id": ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS,
                "value_1_class": "info-text",
                "value_2_class": "info-text"
            },
            {
                "icon": IconID.MONEY_DOLLAR,
                "title": "Value",
                "value_1": "",
                "value_2": "WAITING FOR INPUT...",
                "value_id": ID.MERCHANT_KPI_MERCHANT_VALUE,
                "value_1_class": "info-text",
                "value_2_class": "info-text"
            },
            {
                "icon": IconID.TRANSACTION_BY_CARD,
                "title": "Top User (by Transactions)",
                "value_1": "",
                "value_2": "WAITING FOR INPUT...",
                "value_id": ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS,
                "value_1_class": "info-text",
                "value_2_class": "info-text"
            },
            {
                "icon": IconID.MONEY_WINGS,
                "title": "Top User (by Expenditure)",
                "value_1": "",
                "value_2": "WAITING FOR INPUT...",
                "value_id": ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE,
                "value_1_class": "info-text",
                "value_2_class": "info-text"
            },
        ]

    else:
        count_1 = dm.merchant_tab_data.get_merchant_transactions(merchant)
        value_2 = dm.merchant_tab_data.get_merchant_value(merchant)
        user_3, count_3 = dm.merchant_tab_data.get_user_with_most_transactions_at_merchant(merchant)
        user_4, value_4 = dm.merchant_tab_data.get_user_with_highest_expenditure_at_merchant(merchant)

        no_transactions = count_1 == 0
        transactions_str = "Transaction" if count_1 == 1 else "Transactions"

        kpi_data = [
            {
                "icon": IconID.CHART_PIPE,
                "title": "Transactions",
                "value_1": "",
                "value_2": f"{count_1:,} {transactions_str}" if not no_transactions else "NO DATA",
                "value_id": ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS,
                "value_2_class": "info-text" if no_transactions else ""
            },
            {
                "icon": IconID.MONEY_DOLLAR,
                "title": "Value",
                "value_1": "",
                "value_2": f"${value_2:,.2f}" if not no_transactions else "NO DATA",
                "value_id": ID.MERCHANT_KPI_MERCHANT_VALUE,
                "value_2_class": "info-text" if no_transactions else ""
            },
            {
                "icon": IconID.TRANSACTION_BY_CARD,
                "title": "Top User (by Transactions)",
                "value_1": f"ID {user_3}" if not no_transactions else "",
                "value_2": f"{count_3:,} {transactions_str}" if not no_transactions else "NO DATA",
                "value_id": ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS,
                "value_2_class": "info-text" if no_transactions else ""
            },
            {
                "icon": IconID.MONEY_WINGS,
                "title": "Top User (by Expenditure)",
                "value_1": f"ID {user_4}" if not no_transactions else "",
                "value_2": f"${value_4:,.2f}" if not no_transactions else "NO DATA",
                "value_id": ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE,
                "value_2_class": "info-text" if no_transactions else ""
            },
        ]

    return create_kpi_dashboard(kpi_data)


# === GRAPH ===

def create_merchant_group_distribution_tree_map(dark_mode: bool = const.DEFAULT_DARK_MODE) -> px.treemap:
    """
    Generates a treemap visualization of merchant group distribution.

    This function creates a treemap displaying the distribution of merchant groups
    based on the transaction count. It allows customization of the appearance based
    on whether dark mode is enabled or not.

    Args:
        dark_mode (bool): Determines the color mode of the treemap. If True, the
        treemap text will use white color. If False, it will use black. Defaults to
        False.

    Returns:
        px.treemap: A Plotly Treemap object representing the merchant group
        distribution.
    """
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT

    treemap_df = dm.merchant_tab_data.get_merchant_group_overview(merchant_other_threshold).copy()
    treemap_df["merchant_group"] = treemap_df["merchant_group"].astype(str).str.upper()

    fig = px.treemap(
        treemap_df,
        path=[px.Constant("MERCHANT GROUPS"), "merchant_group"],
        values="transaction_count",
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br><br><b>TRANSACTIONS:</b> %{value}<br><b>SHARE:</b> %{percentEntry:.2%}",
        hovertemplate="<b>%{label}</b><br>💳 <b>TRANSACTIONS:</b> %{value}<br><b>🔢 SHARE:</b> %{percentEntry:.2%}<extra></extra>",
        root_color=const.COLOR_TRANSPARENT,
        tiling_pad=0
    )
    fig.update_layout(
        font=dict(color=text_color),
        margin=dict(t=2, l=2, r=2, b=2),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        showlegend=False,
    )
    return fig


# === CALLBACKS ===

@callback(
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data", allow_duplicate=True),
    Input(ID.MERCHANT_BTN_ALL_MERCHANTS, "n_clicks"),
    Input(ID.MERCHANT_BTN_MERCHANT_GROUP, "n_clicks"),
    Input(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, "n_clicks"),
    prevent_initial_call=True,
)
def set_merchant_tab(n_all, n_group, n_indiv):
    """
    Set the merchant tab based on which button was clicked.

    This callback function determines which merchant tab to activate when one of the merchant-related buttons is
    clicked. The activated tab is returned based on the ID of the button triggering the callback.

    Parameters:
    n_all: int | None
        The number of times the "All Merchants" button has been clicked.
    n_group: int | None
        The number of times the "Merchant Group" button has been clicked.
    n_indiv: int | None
        The number of times the "Individual Merchant" button has been clicked.

    Returns:
    str
        The value of the merchant tab to activate, corresponding to the button
        clicked. Defaults to the value for the "All Merchants" tab if the
        trigger ID does not map to any specific merchant tab.
    """
    trigger_id = ctx.triggered_id
    return ID_TO_MERCHANT_TAB.get(trigger_id, MerchantTab.ALL).value


@callback(
    Output(ID.MERCHANT_BTN_ALL_MERCHANTS, "className"),
    Output(ID.MERCHANT_BTN_MERCHANT_GROUP, "className"),
    Output(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, "className"),
    Output(ID.MERCHANT_GROUP_INPUT_WRAPPER, "style"),
    Output(ID.MERCHANT_INPUT_WRAPPER, "style"),
    Output(ID.MERCHANT_KPI_CONTAINER, "children"),
    Output(ID.MERCHANT_GRAPH_CONTAINER, "figure"),
    Output(ID.MERCHANT_GRAPH_TITLE, "children"),
    Output(ID.MERCHANT_BAR_CHART_SPINNER, "className"),
    Input(ID.MERCHANT_SELECTED_BUTTON_STORE, "data"),
    Input(ID.MERCHANT_INPUT_GROUP_DROPDOWN, "value"),
    Input(ID.MERCHANT_INPUT_MERCHANT_ID, "value"),
    Input(ID.APP_STATE_STORE, "data")
)
def update_merchant(selected, selected_group, selected_merchant_id, app_state):
    """
    Updates the user interface components based on the currently selected merchant
    tab, group, or individual merchant.

    This function handles the dynamic UI updates for the merchant tab, including button styles,
    input visibility, KPI content, graph figures, and titles based on the selected merchant type.

    Arguments:
        selected (str): Identifier for the currently selected merchant type
            (e.g., "all", "group", or "individual"). Defaults to "all" if not provided.
        selected_group (str): The currently selected merchant group from the dropdown.
            Can be None if no group is selected.
        selected_merchant_id (str or int): The identifier for the selected individual merchant.
            Can be None or an invalid input.
        n_clicks_dark (int): Number of times the dark mode toggle button is clicked.
            Odd values indicate dark mode is activated.
        app_state (dict): The current application state containing settings like dark_mode.

    Returns:
        tuple: Contains UI component properties (button classes, styles, content, figures, titles).
    """
    # Set default tab if none selected
    if not selected:
        selected = MerchantTab.ALL.value

    # Get dark mode from app state
    dark_mode = app_state.get("dark_mode", const.DEFAULT_DARK_MODE) if app_state else const.DEFAULT_DARK_MODE

    # Define display styles based on selected tab
    visible_style = {"display": "flex", "width": "100%"}
    hidden_style = {"display": "none", "width": "100%"}

    # Set input wrapper visibility based on selected tab
    group_style = visible_style if selected == MerchantTab.GROUP.value else hidden_style
    indiv_style = visible_style if selected == MerchantTab.INDIVIDUAL.value else hidden_style

    # Initialize default values
    kpi_content = html.Div()
    graph_content = comp_factory.create_empty_figure()
    graph_title = ""
    spinner_class = "map-spinner"

    # Handle content based on selected tab
    if selected == MerchantTab.ALL.value:
        kpi_content = create_all_merchant_kpis()
        graph_content = create_merchant_group_distribution_tree_map(dark_mode=dark_mode)
        graph_title = "MERCHANT GROUP DISTRIBUTION"

    elif selected == MerchantTab.GROUP.value:
        # Get merchant group (selected or default first group)
        merchant_groups = dm.merchant_tab_data.get_all_merchant_groups()
        default_group = merchant_groups[0] if merchant_groups else None
        merchant_group = selected_group or default_group

        if merchant_group:
            kpi_content = create_merchant_group_kpi(merchant_group)
            graph_content = create_merchant_group_line_chart(merchant_group, dark_mode=dark_mode)
            graph_title = f"HISTORY FOR MERCHANT GROUP ", html.Span(f"{merchant_group}", className="green-text")
        else:
            kpi_content = html.Div("NO MERCHANT GROUPS AVAILABLE.")
            graph_title = "NO MERCHANT GROUP SELECTED"

    elif selected == MerchantTab.INDIVIDUAL.value:
        # Convert merchant ID to integer if possible
        merchant = None
        try:
            merchant = int(selected_merchant_id)
        except (ValueError, TypeError):
            pass

        # Create KPI content for the merchant
        kpi_content = create_individual_merchant_kpi(merchant)

        # Create graph content if merchant ID is valid
        if merchant in dm.merchant_tab_data.unique_merchant_ids:
            graph_content, spinner_class = create_individual_merchant_line_chart(merchant, dark_mode=dark_mode)
            graph_title = f"HISTORY FOR MERCHANT ", html.Span(f"{merchant}", className="green-text")
        else:
            graph_title = "HISTORY FOR MERCHANT"
            spinner_class = "map-spinner visible"

    # Return all UI component properties
    return (
        get_option_button_class(MerchantTab.ALL.value, selected),
        get_option_button_class(MerchantTab.GROUP.value, selected),
        get_option_button_class(MerchantTab.INDIVIDUAL.value, selected),
        group_style,
        indiv_style,
        kpi_content,
        graph_content,
        graph_title,
        spinner_class
    )

@callback(
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data", allow_duplicate=True),
    Output(ID.MERCHANT_INPUT_MERCHANT_ID, "value", allow_duplicate=True),
    Output(ID.ACTIVE_TAB_STORE, "data", allow_duplicate=True),
    Output(ID.USER_ID_SEARCH_INPUT, "value", allow_duplicate=True),
    [
        Input(ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP, "n_clicks"),
        Input(ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP, "n_clicks"),
        Input(ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP, "n_clicks"),
        Input(ID.MERCHANT_KPI_USER_HIGHEST_VALUE_IN_GROUP, "n_clicks"),
    ],
    [
        State(ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP, "children"),
        State(ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP, "children"),
        State(ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP, "children"),
        State(ID.MERCHANT_KPI_USER_HIGHEST_VALUE_IN_GROUP, "children"),
    ],
    prevent_initial_call=True,
)
def handle_kpi_click_merchant_group(n1, n2, n3, n4, kpi1, kpi2, kpi3, kpi4):
    """
    Handles user interaction with KPIs related to merchant groups and updates
    the state of the application accordingly. This function manages changes
    triggered by clicks on specific KPI elements and determines appropriate
    IDs for merchants or users based on the provided KPI data.

    The outputs of this callback update the current merchant or user ID in the
    application, as well as the active tab in the user interface. This ensures
    that the UI reflects the correct details and context based on user interactions
    with the KPI elements.

    Args:
        n1: Number of clicks on the 'most frequently merchant' KPI button.
        n2: Number of clicks on the 'highest value merchant' KPI button.
        n3: Number of clicks on the 'most transactions user' KPI button.
        n4: Number of clicks on the 'highest value user' KPI button.
        kpi1: Button child data associated with the 'most frequently merchant' KPI.
        kpi2: Button child data associated with the 'highest value merchant' KPI.
        kpi3: Button child data associated with the 'most transactions user' KPI.
        kpi4: Button child data associated with the 'highest value user' KPI.

    Returns:
        list[Union[no_update, Any]]: The updated states for the merchant-selected button,
        merchant input value, active tab, and user ID search input, based on the triggered input.
    """
    triggered = ctx.triggered_id

    if triggered and n1 < 1 and n2 < 1 and n3 < 1 and n4 < 1:
        return no_update, no_update, no_update, no_update

    def extract_id(kpi_data):
        try:
            children = kpi_data[0]["props"]["children"][1]["props"]["children"][0]["props"]["children"]
            id_str = children[0]["props"].get("children", "")
            return int(id_str.replace("ID", "").strip())
        except Exception as e:
            print(f"Error extracting ID: {e}")
            return None

    if triggered == ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP:
        merchant_id = extract_id(kpi1)
        if merchant_id is not None:
            return MerchantTab.INDIVIDUAL.value, merchant_id, no_update, no_update

    elif triggered == ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP:
        merchant_id = extract_id(kpi2)
        if merchant_id is not None:
            return MerchantTab.INDIVIDUAL.value, merchant_id, no_update, no_update

    elif triggered == ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP:
        user_id = extract_id(kpi3)
        if user_id is not None:
            return no_update, no_update, ID.TAB_USER, user_id

    elif triggered == ID.MERCHANT_KPI_USER_HIGHEST_VALUE_IN_GROUP:
        user_id = extract_id(kpi4)
        if user_id is not None:
            return no_update, no_update, ID.TAB_USER, user_id

    return no_update, no_update, no_update, no_update

@callback(
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data", allow_duplicate=True),
    Output(ID.MERCHANT_INPUT_GROUP_DROPDOWN, "value", allow_duplicate=True),
    Output(ID.ACTIVE_TAB_STORE, "data", allow_duplicate=True),
    Output(ID.USER_ID_SEARCH_INPUT, "value", allow_duplicate=True),
    [
        Input(ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP, "n_clicks"),
        Input(ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP, "n_clicks"),
        Input(ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL, "n_clicks"),
        Input(ID.MERCHANT_KPI_USER_HIGHEST_VALUE_ALL, "n_clicks"),
    ],
    [
        State(ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP, "children"),
        State(ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP, "children"),
        State(ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL, "children"),
        State(ID.MERCHANT_KPI_USER_HIGHEST_VALUE_ALL, "children"),
    ],
    prevent_initial_call=True,
)
def handle_kpi_click_all_merchant_(n1, n2, n3, n4, kpi1, kpi2, kpi3, kpi4):
    """
    Handles user interaction with various merchant KPI buttons in the dashboard. Depending on the triggered
    input, it extracts relevant data from click events and updates the state of the dashboard components.

    Args:
        n1: Number of clicks on the "Most Frequently Merchant Group" KPI button.
        n2: Number of clicks on the "Highest Value Merchant Group" KPI button.
        n3: Number of clicks on the "User Most Transactions (All)" KPI button.
        n4: Number of clicks on the "User Highest Value (All)" KPI button.
        kpi1: Data representing the "Most Frequently Merchant Group" KPI.
        kpi2: Data representing the "Highest Value Merchant Group" KPI.
        kpi3: Data representing the "User Most Transactions (All)" KPI.
        kpi4: Data representing the "User Highest Value (All)" KPI.

    Returns:
        tuple: A tuple of updated states for the dashboard components:
            - ID.MERCHANT_SELECTED_BUTTON_STORE (data)
            - ID.MERCHANT_INPUT_GROUP_DROPDOWN (value)
            - ID.ACTIVE_TAB_STORE (data)
            - ID.USER_ID_SEARCH_INPUT (value)
    """
    triggered = ctx.triggered_id

    def extract_group_label(kpi_data):
        try:
            container = kpi_data[0]["props"]["children"][1]["props"]["children"][0]["props"]["children"]
            return container[0]["props"].get("children", "").strip()
        except Exception:
            return None

    def extract_user_id(kpi_data):
        try:
            container = kpi_data[0]["props"]["children"][1]["props"]["children"][0]["props"]["children"]
            user_str = container[0]["props"].get("children", "").strip()
            return int(user_str.replace("ID", "").strip()) if "ID" in user_str else None
        except Exception:
            return None

    if triggered == ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP:
        group_name = extract_group_label(kpi1)
        return MerchantTab.GROUP.value, group_name, no_update, no_update

    elif triggered == ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP:
        group_name = extract_group_label(kpi2)
        return MerchantTab.GROUP.value, group_name, no_update, no_update

    elif triggered == ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL:
        user_id = extract_user_id(kpi3)
        return no_update, no_update, ID.TAB_USER, user_id

    elif triggered == ID.MERCHANT_KPI_USER_HIGHEST_VALUE_ALL:
        user_id = extract_user_id(kpi4)
        return no_update, no_update, ID.TAB_USER, user_id

    return no_update, no_update, no_update, no_update

# had to use all 4 inputs, otherwise immediate jump to user tab
@callback(
    Output(ID.ACTIVE_TAB_STORE, "data", allow_duplicate=True),
    Output(ID.USER_ID_SEARCH_INPUT, "value", allow_duplicate=True),
    [
        Input(ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS, "n_clicks"),
        Input(ID.MERCHANT_KPI_MERCHANT_VALUE, "n_clicks"),
        Input(ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS, "n_clicks"),
        Input(ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE, "n_clicks"),
    ],
    [
        State(ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS, "children"),
        State(ID.MERCHANT_KPI_MERCHANT_VALUE, "children"),
        State(ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS, "children"),
        State(ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE, "children"),
    ],
    prevent_initial_call=True,
)
def handle_kpi_click_individual_merchant(n1, n2, n3, n4, kpi1, kpi2, kpi3, kpi4):
    """Handles the click events for individual merchant KPIs and updates components based on
    the specific KPI button clicked. This function processes the triggered input, extracts relevant
    user ID from the KPI data, and updates the active tab and user ID search input accordingly.

    Args:
        n1: The number of times the "Merchant Transactions" KPI button is clicked.
        n2: The number of times the "Merchant Value" KPI button is clicked.
        n3: The number of times the "Merchant User Most Transactions" KPI button is clicked.
        n4: The number of times the "Merchant User Highest Value" KPI button is clicked.
        kpi1: The state data of the "Merchant Transactions" KPI button.
        kpi2: The state data of the "Merchant Value" KPI button.
        kpi3: The state data of the "Merchant User Most Transactions" KPI button.
        kpi4: The state data of the "Merchant User Highest Value" KPI button.

    Returns:
        Output: A tuple of the updated active tab and user ID search input value, or `no_update`
        if no valid user ID is extracted.

    Raises:
        None: This function handles exceptions internally and does not raise them.
    """
    triggered = ctx.triggered_id

    if triggered not in [
        ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS,
        ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE,
    ]:
        return no_update, no_update

    def extract_user_id(kpi_data):
        try:
            children = kpi_data[0]["props"]["children"][1]["props"]["children"][0]["props"]["children"]
            id_str = children[0]["props"].get("children", "")
            return int(id_str.replace("ID", "").strip())
        except Exception as e:
            print(f"Error extracting user ID: {e}")
            return None

    if triggered == ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS:
        user_id = extract_user_id(kpi3)
    elif triggered == ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE:
        user_id = extract_user_id(kpi4)
    else:
        user_id = None

    if user_id is not None:
        return ID.TAB_USER, user_id

    return no_update, no_update




