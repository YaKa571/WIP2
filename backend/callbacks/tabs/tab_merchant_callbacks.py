import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, Output, Input, callback, dcc, ctx

import components.constants as const
from backend.data_setup.tabs import tab_merchant_data_setup
from backend.data_setup.tabs.tab_merchant_data_setup import create_merchant_group_line_chart, \
    create_individual_merchant_line_chart
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

"""
Callbacks and factories for tab Merchant.
"""
OPTION_BUTTON_BASE_CLASS = "settings-button-text option-btn"


def get_option_button_class(option_id: str, selected_option: str) -> str:
    """
    Determines the appropriate CSS class for an option button based on whether it is selected.

    Parameters:
    opt : Any
        The current option to evaluate against the selected option.
    selected : bool
        A boolean indicating whether the current option is the selected option.

    Returns:
    str
        The CSS class to apply to the button, indicating its state as either selected
        or not.
    """
    return f"{OPTION_BUTTON_BASE_CLASS} selected" if selected_option == option_id else OPTION_BUTTON_BASE_CLASS


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
    group_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_group()
    group_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_group()
    user_3, count_3 = tab_merchant_data_setup.get_most_user_with_most_transactions_all_merchants()
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_all_merchants()

    kpi_data = [
        {
            "icon": IconID.REPEAT,
            "title": "Most frequently used merchant group",
            "value_1": group_1,
            "value_2": f"{count_1} Transactions",
            "value_id": ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "Merchant group with the highest total transfers",
            "value_1": group_2,
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP
        },
        {
            "icon": IconID.REPEAT,
            "title": "User with most transactions",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3} Transactions",
            "value_id": ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "User with highest Expenditure",
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
    merchant_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_in_group(merchant_group)
    merchant_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_in_group(merchant_group)
    user_3, count_3 = tab_merchant_data_setup.get_user_with_most_transactions_in_group(merchant_group)
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_in_group(merchant_group)

    kpi_data = [
        {
            "icon": IconID.REPEAT,
            "title": "Most frequently used merchant in merchant group",
            "value_1": f"ID {merchant_1}",
            "value_2": f"{count_1} Transactions",
            "value_id": ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "Merchant in group with the highest total transfers",
            "value_1": f"ID {merchant_2}",
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP
        },
        {
            "icon": IconID.REPEAT,
            "title": "User with most transactions in merchant group",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3} Transactions",
            "value_id": ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "User with highest Expenditure in merchant group",
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
    count_1 = tab_merchant_data_setup.get_merchant_transactions(merchant)
    value_2 = tab_merchant_data_setup.get_merchant_value(merchant)
    user_3, count_3 = tab_merchant_data_setup.get_user_with_most_transactions_at_merchant(merchant)
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_at_merchant(merchant)

    kpi_data = [
        {
            "icon": IconID.REPEAT,
            "title": "Transactions",
            "value_1": " ",
            "value_2": f"{count_1} Transactions",
            "value_id": ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "Value",
            "value_1": " ",
            "value_2": f"${value_2:,.2f}",
            "value_id": ID.MERCHANT_KPI_MERCHANT_VALUE
        },
        {
            "icon": IconID.REPEAT,
            "title": "User with most transactions at merchant",
            "value_1": f"ID {user_3}",
            "value_2": f"{count_3} Transactions",
            "value_id": ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS
        },
        {
            "icon": IconID.USER_PAYING,
            "title": "User with highest Expenditure at merchant",
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
    my_merchant_groups = tab_merchant_data_setup.get_all_merchant_groups()
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

    my_treemap_df = tab_merchant_data_setup.get_merchant_group_overview(1000)
    my_treemap_fig = px.treemap(
        my_treemap_df,
        path=[px.Constant("Merchant Groups"), "merchant_group"],
        values="transaction_count",
    )
    my_treemap_fig.update_traces(
        textinfo="label+percent entry",
        hovertemplate="<b>%{label}</b><br>Transactions: %{value}<br>Share: %{percentEntry:.2%}<extra></extra>",
        root_color="rgba(0,0,0,0)"
    )
    my_treemap_fig.update_layout(
        font=dict(color=text_color),
        margin=dict(t=0, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return my_treemap_fig


# === CALLBACKS ===

@callback(
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data"),
    Input(ID.MERCHANT_BTN_ALL_MERCHANTS, "n_clicks"),
    Input(ID.MERCHANT_BTN_MERCHANT_GROUP, "n_clicks"),
    Input(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, "n_clicks"),
    prevent_initial_call=True,
)
def set_merchant_tab(n_all, n_group, n_indiv):
    """
    This function is a callback function used to update the data of a specific output
    based on the triggering input. It determines which merchant tab (e.g., all merchants,
    merchant group, or individual merchant) has been selected based on the triggering
    button's click event and sets the output accordingly.

    Parameters:
        n_all: int
            Number of clicks on the button for all merchants.
        n_group: int
            Number of clicks on the button for merchant groups.
        n_indiv: int
            Number of clicks on the button for individual merchants.

    Returns:
        str
            A string indicating the selected merchant tab. Returns "opt2" for the merchant
            group, "opt3" for the individual merchant, or "opt1" for all merchants.
    """
    if ctx.triggered_id == ID.MERCHANT_BTN_MERCHANT_GROUP:
        return "opt2"
    elif ctx.triggered_id == ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT:
        return "opt3"
    else:
        return "opt1"


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
    Updates the UI components of the merchant section based on user input.

    This callback function dynamically updates the appearance, content, and configuration
    of several UI elements related to merchants. It adapts to the user's selection of specific
    merchant types, merchant groups, or individual merchant IDs. Additionally, supports dark
    mode toggling, which affects the appearance of graphs. The function computes display
    styles, KPI contents, graphical data, and titles for various scenarios, including default
    selections, specific group selections, or individual merchants.

    Parameters
    ----------
    selected : str
        The selected option representing the merchant type. Defaults to "opt1" if not provided.

    selected_group : str
        The name of the merchant group selected from the dropdown. Optional input that might
        influence KPI content and graph data.

    selected_merchant_id : str
        The ID of the merchant as input by the user. Can be converted to an integer for further
        processing.

    n_clicks_dark : int
        The number of clicks on the dark mode toggle button. Odd values indicate dark mode
        should be active, even values indicate light mode.

    Returns
    -------
    tuple
        A tuple containing:
        - className for the "All Merchants" button.
        - className for the "Merchant Group" button.
        - className for the "Individual Merchant" button.
        - CSS style for the merchant group input wrapper.
        - CSS style for the individual merchant input wrapper.
        - Content of the KPI container (can be a table, message, or visualization).
        - Figure data for the graph container (can be empty or populated with visualizations).
        - Title of the current graph being displayed.
    """
    if not selected:
        selected = "opt1"  # Default

    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    group_style = {"display": "flex", "width": "100%"} if selected == "opt2" else {"display": "none", "width": "100%"}
    indiv_style = {"display": "flex", "width": "100%"} if selected == "opt3" else {"display": "none", "width": "100%"}

    if selected == "opt1":
        kpi_content = create_all_merchant_kpis()
        graph_content = create_merchant_group_distribution_tree_map(dark_mode=dark_mode)
        graph_title = "Merchant Group Distribution"
    elif selected == "opt2":
        merchant_group = selected_group or (
            tab_merchant_data_setup.get_all_merchant_groups()[0]
            if tab_merchant_data_setup.get_all_merchant_groups() else None)
        kpi_content = create_merchant_group_kpi(merchant_group) if merchant_group else html.Div(
            "No merchant groups available.")
        graph_content = create_merchant_group_line_chart(
            merchant_group) if merchant_group else comp_factory.create_empty_figure()
        graph_title = f"History for Merchant Group: {merchant_group}" if merchant_group else "No Merchant Group Selected"
    elif selected == "opt3":
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
        get_option_button_class("opt1", selected),
        get_option_button_class("opt2", selected),
        get_option_button_class("opt3", selected),
        group_style,
        indiv_style,
        kpi_content,
        graph_content,
        graph_title
    )
