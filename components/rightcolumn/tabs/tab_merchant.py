import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc, Output, Input, callback


from backend.callbacks.tabs import tab_merchant_callbacks
from backend.data_setup.tabs import tab_merchant_data_setup
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import Icons, IconID

COLOR_BLUE_MAIN = "#2563eb"

# Info: Edit grid layout in assets/css/tabs.css


def create_merchant_content():
    return html.Div(
        className="tab-content-inner merchant-tab",
        children=[

            create_merchant_heading(),
            create_merchant_input_container(),
            create_merchant_kpi(),
            create_merchant_graph()

        ])


def create_merchant_heading() -> html.Div:
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Button('All Merchants', id=ID.MERCHANT_BTN_ALL_MERCHANTS, n_clicks=0, className='option-btn'),
                        html.Button('Merchant Group', id=ID.MERCHANT_BTN_MERCHANT_GROUP, n_clicks=0, className='option-btn'),
                        html.Button('Merchant', id=ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, n_clicks=0, className='option-btn'),
                    ], className='button-radio-wrapper'),

                ], width = 9),
                dbc.Col([
                    html.Div(html.P("Button Map")),
                ], width=2),
                dbc.Col([
                    comp_factory.create_info_icon(ID.MERCHANT_INFO_ICON),
                    dbc.Tooltip(
                        target=ID.MERCHANT_INFO_ICON,
                        is_open=False,
                        placement="bottom-end",
                        children=[
                            "Placeholder for",
                            html.Br(),
                            "the tooltip",
                            html.Br(),
                            "..."
                        ]),
                ], width = 1),
            ]),



        ])
def create_merchant_input_container():
    return html.Div(
        dbc.Row([
            dbc.Col([
                html.Div(id=ID.MERCHANT_INPUT_CONTAINER)
            ])
        ])
    )

def create_merchant_kpi():
    return dbc.Row([
        html.Div(id=ID.MERCHANT_KPI_CONTAINER)
    ])


def create_merchant_graph():
    """
    Creates a styled card container for displaying the merchant transaction graph.

    This function returns a Dash HTML Div that contains a Bootstrap card layout.
    The card includes a header with a dynamic title and an icon, and a body section
    with a Dash Graph component. The actual graph content is expected to be
    updated dynamically via a callback.

    Returns:
        dash.html.Div: A styled card layout with a placeholder for a merchant transaction graph.
    """
    return html.Div(
        className="flex-wrapper flex-fill",
        children=[
            dbc.Card(
                className="graph-card with-bar-chart",
                style={"flex": "1 1 0", "height": "100%", "minHeight": "400px"},
                children=[
                    dbc.CardHeader(
                        children=[
                            comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-small"),
                            html.H3(id=ID.MERCHANT_GRAPH_TITLE, className="graph-title")
                        ]
                    ),
                    dbc.CardBody(
                        style={"height": "100%", "padding": "1rem"},
                        children=[
                            dcc.Graph(
                                id=ID.MERCHANT_GRAPH_CONTAINER,
                                className="bar-chart",
                                config={"displayModeBar": True, "displaylogo": False},
                                style={
                                    "height": "350px",  # fix height to ensure rendering
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )




