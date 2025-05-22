from frontend.component_ids import ID
from dash import html, Output, Input, callback, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from backend.data_setup.tabs import tab_merchant_data_setup
from components.factories import component_factory as comp_factory
from frontend.icon_manager import Icons, IconID
COLOR_BLUE_MAIN = "#2563eb"
"""
callbacks of tab Merchant
"""
@callback(
    Output(ID.MERCHANT_BTN_ALL_MERCHANTS, 'className'),
    Output(ID.MERCHANT_BTN_MERCHANT_GROUP, 'className'),
    Output(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'className'),
    Output(ID.MERCHANT_KPI_CONTAINER, 'children'),
    Output(ID.MERCHANT_GRAPH_CONTAINER, 'figure'),
    Input(ID.MERCHANT_BTN_ALL_MERCHANTS, 'n_clicks'),
    Input(ID.MERCHANT_BTN_MERCHANT_GROUP, 'n_clicks'),
    Input(ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, 'n_clicks'),
)
def update_merchant(n1, n2, n3):
    buttons = {'opt1': n1, 'opt2': n2, 'opt3': n3}
    selected = max(buttons, key=buttons.get)

    def cls(opt): return 'option-btn selected' if selected == opt else 'option-btn'

    if selected == 'opt1':
        kpi_content = create_all_merchant_kpis()
        graph_content = create_merchant_group_distribution_heat_map()
    else:
        kpi_content = html.Div()
        graph_content = html.Div()

    return cls('opt1'), cls('opt2'), cls('opt3'), kpi_content, graph_content

def create_all_merchant_kpis():
    group_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_group()
    count_1 = str(count_1) + " Transactions"
    group_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_group()
    value_2 = "$" + str(value_2)
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
        ],
            className="flex-wrapper"
        )
    ])

def create_merchant_group_distribution_heat_map():
        my_treemap_df = tab_merchant_data_setup.get_merchant_group_overview(1000)

        my_treemap_fig = px.treemap(
            my_treemap_df,
            path=["merchant_group"],
            values="transaction_count",
            title="Merchant Group Distribution",
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
