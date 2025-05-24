import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.callbacks.tabs import tab_cluster_callbacks
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID
from components.constants import COLOR_BLUE_MAIN

def create_cluster_content():
    """
    Generates the content layout for the cluster tab.

    This function assembles and returns the Div element comprising the components
    required to construct the cluster tab interface. The components are organized
    as a heading, control elements, and visualization section within the Div.

    Returns:
        html.Div: A Div element containing all the components of the cluster tab.
    """
    return html.Div(
        className="tab-content-inner cluster-tab",
        children=[
            html.P("Cluster Tab wird neu aufgesetzt, Finger weg"),

            create_cluster_heading(),
            create_cluster_control_merchant_group(),

            dcc.Graph(id=ID.CLUSTER_GRAPH),
            html.Div(id=ID.CLUSTER_LEGEND)
        ]
    )

def create_cluster_heading():
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Button('Transactions', id=ID.CLUSTER_BTN_TRANSACTIONS, n_clicks=0,
                                    className='option-btn'),
                        html.Button('Value', id=ID.CLUSTER_BTN_VALUE, n_clicks=0,
                                    className='option-btn'),
                        html.Button('Inc vs Exp', id=ID.CLUSTER_BTN_INC_VS_EXP, n_clicks=0,
                                    className='option-btn'),
                    ], className='button-radio-wrapper'),

                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Button('All', id=ID.CLUSTER_BTN_ALL_AGES, n_clicks=0,
                                    className='option-btn'),
                        html.Button('Age Groups', id=ID.CLUSTER_BTN_AGE_GROUP, n_clicks=0,
                                    className='option-btn'),
                    ], className='button-radio-wrapper'),

                ], width=4),
                dbc.Col([
                    html.Div(html.P("Button Map")),
                ], width=2),

            ]),
            comp_factory.create_info_icon(ID.CLUSTER_INFO_ICON),
            dbc.Tooltip(
                target=ID.CLUSTER_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                className="enhanced-tooltip",
                children=[
                    "TODO",
                    html.Br(),
                    "based on new design",
                ]),

        ])

def create_cluster_control_merchant_group():
    return html.Div(
        dbc.Row([
            dbc.Col([
                html.Div(
                    children=[tab_cluster_callbacks.get_cluster_merchant_group_input_container()],
                    id=ID.CLUSTER_CONTROL_MERCHANT_GROUP_DROPDOWN,
                )
            ])
        ])
    )