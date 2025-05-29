from enum import Enum

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, Output, Input, callback, dcc, ctx

import components.constants as const
from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from components.tabs.tab_merchant_components import create_merchant_group_line_chart, \
    create_individual_merchant_line_chart
from frontend.component_ids import ID
from frontend.icon_manager import IconID

# Initialize DataManager instance
dm = DataManager.get_instance()

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

def create_kpi_card(icon, title, value_1, value_2, value_id):
    """
    Creates a KPI (Key Performance Indicator) card component with an icon, title,
    and two value fields. The card is styled with predefined CSS classes and allows
    dynamic updates using a specified value ID.

    Parameters:
        icon: str
            The icon displayed in the card header. Should correspond to a supported
            icon identifier.
        title: str
            The title of the KPI card displayed in the card header.
        value_1: str
            The primary value displayed inside the KPI card body.
        value_2: str
            The secondary value displayed underneath the primary value in the card body.
        value_id: str
            Unique identifier for the card's value container, used for dynamic updates.

    Returns:
        dbc.Card
            A Dash Bootstrap Card component styled and populated with the
            specified content.
    """
    return dbc.Card(
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
                        id=value_id,
                        children=[

                            html.P(value_1, className="kpi-card-value"),
                            html.P(value_2, className="kpi-card-value kpi-number-value")

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
    user_3, count_3 = dm.merchant_tab_data.get_most_user_with_most_transactions_all_merchants()
    user_4, value_4 = dm.merchant_tab_data.get_user_with_highest_expenditure_all_merchants()

    kpi_data = [
        {
            "icon": IconID.CHART_PIPE,
            "title": "Top Merchant Group (by Transactions)",
            "value_1": group_1,
            "value_2": f"{count_1} Transactions",
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
            "value_2": f"{count_3} Transactions",
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
            "value_2": f"{count_1} Transactions",
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
            "value_2": f"{count_3} Transactions",
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


def create_individual_merchant_kpi(merchant: int):
    """
    Generate individual Key Performance Indicators (KPIs) for a merchant by collecting relevant transaction and
    user data.

    Args:
        merchant (str): A unique identifier for the merchant whose KPIs are to be generated.

    Returns:
        dict: A dashboard representation of the merchant's KPIs, formatted for display.

    Raises:
        None
    """
    count_1 = dm.merchant_tab_data.get_merchant_transactions(merchant)
    value_2 = dm.merchant_tab_data.get_merchant_value(merchant)
    user_3, count_3 = dm.merchant_tab_data.get_user_with_most_transactions_at_merchant(merchant)
    user_4, value_4 = dm.merchant_tab_data.get_user_with_highest_expenditure_at_merchant(merchant)

    kpi_data = [
        {
            "icon": IconID.CHART_PIPE,
            "title": "Transactions",
            "value_1": " ",
            "value_2": f"{count_1} Transactions",
            "value_id": ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS
        },
        {
            "icon": IconID.MONEY_DOLLAR,
            "title": "Value",
            "value_1": " ",
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_MERCHANT_VALUE
        },
        {
            "icon": IconID.TRANSACTION_BY_CARD,
            "title": "Top User (by Transactions)",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3} Transactions",
            "value_id": ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS
        },
        {
            "icon": IconID.MONEY_WINGS,
            "title": "Top User (by Expenditure)",
            "value_1": f"ID {user_4}",
            "value_2": f"${value_4:,.2f}",
            "value_id": ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE
        },
    ]
    return create_kpi_dashboard(kpi_data)


# === INPUT CONTAINERS ===

def get_merchant_group_input() -> dcc.Dropdown:
    """
    Generates a Dash Dropdown component for selecting merchant groups.

    This function fetches a list of all available merchant groups and creates a Dropdown
    component with them as selectable options. If no merchant groups are available, the
    Dropdown will not set a default selection.

    Returns:
        dcc.Dropdown: A Dash Dropdown component configured with the available merchant
        groups.

    """
    my_merchant_groups = dm.merchant_tab_data.get_all_merchant_groups()
    options = [{'label': group, 'value': group} for group in my_merchant_groups]
    default_value = my_merchant_groups[0] if my_merchant_groups else None

    return dcc.Dropdown(
        id=ID.MERCHANT_INPUT_GROUP_DROPDOWN,
        className="settings-dropdown settings-text-centered",
        options=options,
        value=default_value,
        placeholder="Choose a Merchant Group...",
        searchable=True,
        clearable=False,
        multi=False,
        style={"width": "100%"}
    )


def get_merchant_id_input() -> dcc.Input:
    """
    Generate an Input component for entering a Merchant ID.

    The function creates and returns a Dash Core Components (dcc) Input
    element configured for accepting a numeric Merchant ID input. Provides
    default value, styles, and a placeholder for user guidance.

    Returns
    -------
    dcc.Input
        A Dash Input component preconfigured for numeric Merchant ID input
        with specified ID, class name, default value, placeholder text, and
        style attributes.
    """
    return dcc.Input(
        id=ID.MERCHANT_INPUT_MERCHANT_ID,
        className="search-bar-input no-spinner",
        type="number",
        autoComplete="off",
        value="50783",
        placeholder="Enter Merchant ID...",
        style={"width": "100%"}
    )


# === GRAPH ===

def create_merchant_group_distribution_tree_map(dark_mode: bool = False) -> px.treemap:
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

    treemap_df = dm.merchant_tab_data.get_merchant_group_overview(1000).copy()
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
    Input(ID.MERCHANT_SELECTED_BUTTON_STORE, "data"),
    Input(ID.MERCHANT_INPUT_GROUP_DROPDOWN, "value"),
    Input(ID.MERCHANT_INPUT_MERCHANT_ID, "value"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
)
def update_merchant(selected, selected_group, selected_merchant_id, n_clicks_dark):
    """
    Updates the user interface components based on the currently selected merchant
    tab, group, or individual merchant. This function updates visual elements like
    button styles, visibility of input wrappers, KPI content, graph figures, and
    graph titles depending on the selection. The function also considers dark mode
    toggle state to adjust display content accordingly.

    Arguments:
        selected (str): Identifier for the currently selected merchant type
            (e.g., "all", "group", or "individual"). Defaults to "all" if not
            provided.
        selected_group (str): The currently selected merchant group from the
            dropdown input. Can be None if no group is selected.
        selected_merchant_id (str or int): The identifier or value for the
            selected individual merchant. Can be None or an invalid input (e.g.,
            empty string).
        n_clicks_dark (int): Number of times the dark mode toggle button is
            clicked. Odd values indicate dark mode is activated; even or zero
            values indicate light mode.

    Returns:
        tuple: Contains the following outputs:
            - className (str): The CSS class name for the "All Merchants" button.
            - className (str): The CSS class name for the "Merchant Group" button.
            - className (str): The CSS class name for the "Individual Merchant"
              button.
            - style (dict): The style properties for the "Merchant Group" input
              wrapper.
            - style (dict): The style properties for the "Individual Merchant"
              input wrapper.
            - children: The content of the KPI container, usually dynamically
              generated components or a placeholder message.
            - figure: The figure content for the graph, rendered differently based
              on the selected merchant type and data availability.
            - children (str): The title of the graph, indicating its purpose or
              scope based on the selection (e.g., merchant group, individual
              merchant).
    """
    if not selected:
        selected = MerchantTab.ALL.value  # Default

    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    group_style = {"display": "flex", "width": "100%"} if selected == MerchantTab.GROUP.value else {"display": "none",
                                                                                                    "width": "100%"}
    indiv_style = {"display": "flex", "width": "100%"} if selected == MerchantTab.INDIVIDUAL.value else {
        "display": "none", "width": "100%"}

    if selected == MerchantTab.ALL.value:
        kpi_content = create_all_merchant_kpis()
        graph_content = create_merchant_group_distribution_tree_map(dark_mode=dark_mode)
        graph_title = "Merchant Group Distribution"
    elif selected == MerchantTab.GROUP.value:
        merchant_group = selected_group or (
            dm.merchant_tab_data.get_all_merchant_groups()[0]
            if dm.merchant_tab_data.get_all_merchant_groups() else None)
        kpi_content = create_merchant_group_kpi(merchant_group) if merchant_group else html.Div(
            "No merchant groups available.")
        graph_content = create_merchant_group_line_chart(
            merchant_group) if merchant_group else comp_factory.create_empty_figure()
        graph_title = f"History for Merchant Group: {merchant_group}" if merchant_group else "No Merchant Group Selected"
    elif selected == MerchantTab.INDIVIDUAL.value:
        try:
            merchant = int(selected_merchant_id)
        except (ValueError, TypeError):
            merchant = None
        if merchant:
            kpi_content = create_individual_merchant_kpi(merchant)
            graph_content = create_individual_merchant_line_chart(merchant)
            graph_title = f"History for Merchant: {merchant}"
        else:
            kpi_content = html.Div("Invalid or no Merchant ID entered.")
            graph_content = comp_factory.create_empty_figure()
            graph_title = "Invalid Merchant ID"
    else:
        kpi_content = html.Div()
        graph_content = comp_factory.create_empty_figure()
        graph_title = ""

    return (
        get_option_button_class(MerchantTab.ALL.value, selected),
        get_option_button_class(MerchantTab.GROUP.value, selected),
        get_option_button_class(MerchantTab.INDIVIDUAL.value, selected),
        group_style,
        indiv_style,
        kpi_content,
        graph_content,
        graph_title
    )
