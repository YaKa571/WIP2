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

def create_merchant_kpi():
    return dbc.Row([
        html.Div(id=ID.MERCHANT_KPI_CONTAINER)
    ])


def create_merchant_graph():
    return dbc.Row([
        dcc.Graph(
            id=ID.MERCHANT_GRAPH_CONTAINER,
            style={"height": "100%", "minHeight": "300px", "width": "100%"}
        )
    ])


