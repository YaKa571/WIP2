from dash import html, dcc
from frontend.component_ids import ID
from components.factories import component_factory as comp_factory
from frontend.icon_manager import Icons, IconID
import dash_bootstrap_components as dbc

COLOR_BLUE_MAIN = "#0d6efd"
# TODO: Free...(Yannic): Idee untere Teil der Seite wie in Skizze, oben Verteilung der Händlerkategorien und Aufschlüsselung (evtl. als Popup)
def create_merchant_content():
    return html.Div(
        [
            create_merchant_heading(),
            # top: general data
            create_merchant_general(),
            # bottom: individual merchant data
            create_merchant_individual()
        ],
        className="tab-content-inner"
    )

def create_merchant_heading():
    return html.Div(
        children=[
                dbc.Col(width=4),
                dbc.Col(html.H4("Merchant", id=ID.MERCHANT_HEADING, className="text-center"),
                        width=4),
                dbc.Col(
                    html.Div([
                        html.I(className="bi bi-info-circle-fill", id=ID.MERCHANT_INFO_ICON),
                        dbc.Tooltip(
                            children=[
                                # TODO: tooltip
                                "TODO",
                                html.Br(),
                                "Tooltip"
                            ],
                            target=ID.MERCHANT_INFO_ICON,
                            placement="bottom-end"
                        )
                    ], className="d-flex justify-content-end"),
                    width=4
                )
        ],
        # TODO: maybe custom css class
        className="tab-home-heading-wrapper"
    )

def create_merchant_general():
    return dbc.Row([
        html.P("general merchant data"),
        create_merchant_kpis(),
        html.Hr()
    ])

def create_merchant_individual():
    return dbc.Row([
        html.P("individual merchant data"),
        # searchbar for Merchant ID
        html.Div(
            [
                html.Img(src=Icons.get_icon(IconID.LENS_SEARCH), className="search-icon"),
                dcc.Input(
                    id=ID.MERCHANT_ID_SEARCH,
                    type='text',
                    placeholder='Search by Merchant ID',
                    className='search-input',
                )
            ],
            className="search-wrapper p-2 flex-grow-1 me-2"
        ),
    ])

def create_merchant_kpis():
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
                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")
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
                            html.P("", className="kpi-card-value"),
                            html.P("", className="kpi-card-value kpi-number-value")
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

def get_most_frequently_used_merchant_group():
    group_return = "group"
    count_return = "count"
    return group_return, count_return

def get_highest_value_merchant_group():
    group_return = "group"
    value_return = "value"
    return group_return, value_return

