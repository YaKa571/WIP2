from backend.data_setup.tabs.tab_merchant_data_setup import create_merchant_group_line_chart, \
    create_individual_merchant_line_chart
from frontend.component_ids import ID
from dash import html, Output, Input, callback, dcc, State
import dash_bootstrap_components as dbc
import plotly.express as px
from backend.data_setup.tabs import tab_merchant_data_setup
from components.factories import component_factory as comp_factory
from frontend.icon_manager import Icons, IconID
import plotly.graph_objects as go
from components.constants import COLOR_BLUE_MAIN

"""
callbacks of tab Merchant
"""
@callback(
    Output(ID.MERCHANT_BTN_ALL_MERCHANTS, 'className'),
    Output(ID.MERCHANT_BTN_MERCHANT_GROUP, 'className'),
    Output(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'className'),
    Output(ID.MERCHANT_INPUT_CONTAINER, 'children'),
    Output(ID.MERCHANT_KPI_CONTAINER, 'children'),
    Output(ID.MERCHANT_GRAPH_CONTAINER, 'figure'),
    Output(ID.MERCHANT_GRAPH_TITLE, 'children'),
    Input(ID.MERCHANT_BTN_ALL_MERCHANTS, 'n_clicks'),
    Input(ID.MERCHANT_BTN_MERCHANT_GROUP, 'n_clicks'),
    Input(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'n_clicks'),
)
def update_merchant(n1, n2, n3):
    buttons = {'opt1': n1, 'opt2': n2, 'opt3': n3}
    selected = max(buttons, key=buttons.get)

    def cls(opt): return 'option-btn selected' if selected == opt else 'option-btn'

    if selected == 'opt1':
        merchant_input_container = html.P("")
        kpi_content = create_all_merchant_kpis()
        graph_content = create_merchant_group_distribution_tree_map()
        graph_title = "Merchant Group Distribution"
    elif selected == 'opt2':
        merchant_input_container = get_merchant_group_input_container()
        merchant_group = "Grocery Stores, Supermarkets" # mcc: 5411 ID.MERCHANT_INPUT TODO
        kpi_content = create_merchant_group_kpi(merchant_group)
        graph_content = create_merchant_group_line_chart(merchant_group)
        graph_title = f"History for Merchant Group: {merchant_group}"
    elif selected == 'opt3':
        merchant_input_container = get_merchant_input_container()
        merchant = 50783 # ID.MERCHANT_INPUT TODO
        kpi_content = create_individual_merchant_kpi(merchant)
        graph_content = create_individual_merchant_line_chart(merchant)
        graph_title = f"History for Merchant: {merchant}"
    else:
        merchant_input_container = html.P("No Input Container")
        kpi_content = html.Div()
        graph_content = go.Figure()
        graph_title = ""

    return cls('opt1'), cls('opt2'), cls('opt3'),merchant_input_container, kpi_content, graph_content, graph_title

# input for opt2
def get_merchant_group_input_container():
    """
        Creates a dropdown input container for selecting a merchant group.

        Retrieves all merchant groups using the tab_merchant_data_setup module, and
        generates a dropdown component with these groups as selectable options.
        The first merchant group is set as the default selected value if available.

        Returns:
            html.Div: A Div containing a label and a Dash Dropdown component for merchant groups.
        """
    my_merchant_groups = tab_merchant_data_setup.get_all_merchant_groups()
    options = [{'label': group, 'value': group} for group in my_merchant_groups]

    default_value = my_merchant_groups[0] if my_merchant_groups else None

    return html.Div([
        html.Label("Select Merchant Group:", className="dropdown-label"),
        dcc.Dropdown(
            id=ID.MERCHANT_INPUT_GROUP_DROPDOWN,
            options=options,
            value=default_value,
            placeholder="Choose a merchant group...",
            searchable=True,
            multi=False,
            style={"width": "100%"}
        )
    ],
        className="dropdown-container"
    )

# input for opt3
def get_merchant_input_container():
    """
        Creates a text input container for entering a merchant ID.

        Provides a labeled text input field pre-filled with a default merchant ID value.
        The user can enter or modify the merchant ID as needed.

        Returns:
            html.Div: A Div containing a label and a Dash Input component for merchant ID.
        """
    default_merchant_id = 50783  # Default ID

    return html.Div([
        html.Label("Enter Merchant ID:", className="input-label"),
        dcc.Input(
            id=ID.MERCHANT_INPUT_MERCHANT_ID,
            type="text",
            value=str(default_merchant_id),
            placeholder="Enter Merchant ID...",
            style={"width": "100%", "padding": "5px", "fontSize": "16px"}
        )
    ],
        className="input-container"
    )

def create_all_merchant_kpis():
    """
        Create a dashboard component displaying key merchant-related KPIs.

        This function collects aggregated merchant data including:
            - The most frequently used merchant group.
            - The merchant group with the highest total transaction value.
            - The user with the most transactions across all merchants.
            - The user with the highest total expenditure across all merchants.

        The KPIs are displayed using Bootstrap Cards and formatted with icons and labels
        for visual clarity.

        Returns:
            html.Div: A Dash HTML Div element containing four KPI cards in a flex layout.
        """
    group_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_group()
    count_1 = str(count_1) + " Transactions"
    group_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_group()
    value_2 = "$" + str(value_2)
    user_3, count_3 = tab_merchant_data_setup.get_most_user_with_most_transactions_all_merchants()
    user_3 = "ID " + str(user_3)
    count_3 = str(count_3) + " Transactions"
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_all_merchants()
    user_4 = "ID " + str(user_4)
    value_4 = "$" + str(value_4)

    return html.Div(children=[
        html.Div(children=[
            # KPI 1: Most frequently used merchant group
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("Most frequently used merchant group", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(group_1, className="kpi-card-value"),
                            html.P(count_1, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 2: Merchant group with the highest total transfers
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("Merchant group with the highest total transfers", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(group_2, className="kpi-card-value"),
                            html.P(value_2, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 3: User with most transactions (all merchants)
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("User with most transactions", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_3, className="kpi-card-value"),
                            html.P(count_3, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_ALL
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 4: User with the highest value (all merchants)
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("User with highest Expenditure", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_4, className="kpi-card-value"),
                            html.P(value_4, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_USER_HIGHEST_VALUE_ALL
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
        ],
            className="flex-wrapper"
        )
    ])

def create_merchant_group_distribution_tree_map():
    """
           Generate a treemap showing the distribution of merchant groups by transaction volume.

           The function uses a predefined transaction threshold to separate large merchant groups
           from smaller ones. Groups below the threshold are aggregated under an "Other" category.
           A Plotly treemap is then created to visualize the relative contribution of each group.

           Returns:
               plotly.graph_objs._figure.Figure: A Plotly treemap figure for merchant group distribution.
           """
    my_treemap_df = tab_merchant_data_setup.get_merchant_group_overview(1000)

    my_treemap_fig = px.treemap(
        my_treemap_df,
        path=["merchant_group"],
        values="transaction_count",
        # title="Merchant Group Distribution",
    )

    my_treemap_fig.update_traces(
        textinfo="label+percent entry",
        hovertemplate="<b>%{label}</b><br>Transactions: %{value}<br>Share: %{percentEntry:.2%}<extra></extra>",
        root_color="rgba(0,0,0,0)"
    )
    my_treemap_fig.update_layout(
        margin=dict(t=20, l=0, r=0, b=0),
        showlegend=False
    )

    return my_treemap_fig

def create_merchant_group_kpi(merchant_group):
    """
       Create a KPI dashboard for a given merchant group.

       This function generates a set of KPI cards displaying key statistics for the specified
       merchant group, including:
       - The most frequently used merchant
       - The merchant with the highest transaction value
       - The user with the most transactions within the group
       - The user with the highest total expenditure within the group

       Args:
           merchant_group (str): The name or identifier of the merchant group.

       Returns:
           html.Div: A Dash HTML Div component containing the KPI cards.
       """
    merchant_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_in_group(merchant_group)
    merchant_1 = "ID " + str(merchant_1)
    count_1 = str(count_1) + " Transactions"
    merchant_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_in_group(merchant_group)
    merchant_2 = "ID " + str(merchant_2)
    value_2 = "$" + str(value_2)
    user_3, count_3 = tab_merchant_data_setup.get_user_with_most_transactions_in_group(merchant_group)
    user_3 = "ID " + str(user_3)
    count_3 = str(count_3) + " Transactions"
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_in_group(merchant_group)
    user_4 = "ID " + str(user_4)
    value_4 = "$" + str(value_4)

    return html.Div(children=[
        html.Div(children=[
            # KPI 1: Most frequently used merchant in group
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("Most frequently used merchant in merchant group", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(merchant_1, className="kpi-card-value"),
                            html.P(count_1, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_IN_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 2: Merchant in group with the highest total transfers
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("Merchant in merchant group with the highest total transfers", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(merchant_2, className="kpi-card-value"),
                            html.P(value_2, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_IN_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 3: User with most transactions in group
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("User with most transactions in merchant group", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_3, className="kpi-card-value"),
                            html.P(count_3, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_USER_MOST_TRANSACTIONS_IN_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 4: User with the highest value in group
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("User with highest Expenditure in merchant group", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_4, className="kpi-card-value"),
                            html.P(value_4, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_USER_HIGHEST_VALUE_IN_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
        ],
            className="flex-wrapper"
        )
    ])

def create_individual_merchant_kpi(merchant):
    """
        Create a KPI dashboard for an individual merchant.

        This function generates a set of KPI cards for a specific merchant, including:
        - Total number of transactions at the merchant
        - Total value of all transactions at the merchant
        - The user with the most transactions at the merchant
        - The user with the highest total expenditure at the merchant

        Args:
            merchant (str): The name or identifier of the merchant.

        Returns:
            html.Div: A Dash HTML Div component containing the KPI cards.
        """
    count_1 = str(tab_merchant_data_setup.get_merchant_transactions(merchant)) + " Transactions"
    value_2 = "$" + str(tab_merchant_data_setup.get_merchant_value(merchant))
    user_3, count_3 = tab_merchant_data_setup.get_user_with_most_transactions_at_merchant(merchant)
    user_3 = "ID " + str(user_3)
    count_3 = str(count_3) + " Transactions"
    user_4, value_4 = tab_merchant_data_setup.get_user_with_highest_expenditure_at_merchant(merchant)
    user_4 = "ID " + str(user_4)
    value_4 = "$" + str(value_4)

    return html.Div(children=[
        html.Div(children=[
            # KPI 1: transactions at merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("Transactions", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(" ", className="kpi-card-value"),
                            html.P(count_1, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MERCHANT_TRANSACTIONS
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 2: value at Merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("Value", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(" ", className="kpi-card-value"),
                            html.P(value_2, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MERCHANT_VALUE
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 3: User with most transactions at merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("User with most transactions at merchant", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_3, className="kpi-card-value"),
                            html.P(count_3, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MERCHANT_USER_MOST_TRANSACTIONS
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 4: User with the highest value at merchant
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("User with highest Expenditure at merchant", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(user_4, className="kpi-card-value"),
                            html.P(value_4, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MERCHANT_USER_HIGHEST_VALUE
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
        ],
            className="flex-wrapper"
        )
    ])




