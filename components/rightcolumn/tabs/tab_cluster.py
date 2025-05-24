import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.callbacks.tabs import tab_cluster_callbacks
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID
from components.constants import COLOR_BLUE_MAIN

def create_cluster_content():
    """
        Creates the main container Div for the cluster tab content,
        including heading, age group switch, merchant group filter,
        and cluster visualization components.

        Returns:
            html.Div: The complete cluster tab content layout.
        """
    return html.Div(
        className="tab-content-inner cluster-tab",
        children=[

            create_cluster_heading(),
            create_cluster_age_group_switch(),
            create_cluster_control_merchant_group(),
            create_cluster_visualization()

        ]
    )
def create_cluster_age_group_switch():
    """
        Creates a UI component with buttons to toggle between viewing
        data for all ages or segmented by age groups.

        Returns:
            html.Div: A Div containing the age group toggle buttons.
        """
    return html.Div(
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Button('All Ages', id=ID.CLUSTER_BTN_ALL_AGES, n_clicks=0,
                                className='option-btn'),
                    html.Button('Age Groups', id=ID.CLUSTER_BTN_AGE_GROUP, n_clicks=0,
                                className='option-btn'),
                ], className='button-radio-wrapper'),

            ]),
        ])

    )

def create_cluster_heading():
    """
        Creates the header section of the cluster tab including buttons
        for selecting the clustering mode (Total Value, Average Value,
        Income vs Expenses) and an info icon with tooltip explaining usage.

        Returns:
            html.Div: The cluster tab header layout.
        """
    return html.Div(
        className="tab-heading-wrapper",
        children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Button('Total Value', id=ID.CLUSTER_BTN_TOTAL_VALUE, n_clicks=0,
                                    className='option-btn'),
                        html.Button('Average Value', id=ID.CLUSTER_BTN_AVERAGE_VALUE, n_clicks=0,
                                    className='option-btn'),
                        html.Button('Inc vs Exp', id=ID.CLUSTER_BTN_INC_VS_EXP, n_clicks=0,
                                    className='option-btn'),
                    ], className='button-radio-wrapper'),

                ], width=10),

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
                    "Switch between plotting ",
                    html.Br(),
                    "Total Value/Average Value",
                    html.Br(),
                    "or choose Income vs. Expenses",
                    html.Hr(),
                    "choose to show Plot for all Ages",
                    html.Br(),
                    "or show Plot for different Age Groups",
                    html.Hr(),
                    "Choose Filter for Merchant Groups",
                    html.Br(),
                    "using Dropdown"
                ]),

        ])

def create_cluster_control_merchant_group():
    """
        Creates the container Div that holds the merchant group filter dropdown.
        This allows filtering cluster data by merchant groups.

        Returns:
            html.Div: The container for merchant group dropdown control.
        """
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

def create_cluster_visualization():
    """
        Creates the visualization layout for the cluster tab including two cards:
        one for the cluster scatter plot graph and one for the cluster legend.

        Returns:
            html.Div: The visualization container with graph and legend cards.
        """
    return html.Div(
        className="flex-wrapper flex-fill",
        children=[

            dbc.Card(
                className="graph-card with-bar-chart",
                style={"flex": "2 1 0"},
                children=[

                    dbc.CardHeader(
                        children=[

                            comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-small"),
                            html.P("Cluster Visualization", className="graph-card-title")

                        ]
                    ),

                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                id=ID.CLUSTER_GRAPH,
                                className="bar-chart",
                                config={"displayModeBar": True, "displaylogo": False},
                                responsive=True,
                                style={"minHeight": "400px", "height": "100%"}
                            )

                        ]
                    )
                ]
            ),

            dbc.Card(
                className="graph-card",
                style={"flex": "1 1 0"},
                children=[

                    dbc.CardHeader(
                        children=[

                            comp_factory.create_icon(IconID.LEGEND, cls="icon icon-small"),
                            html.P("Cluster Legend", className="graph-card-title")

                        ]
                    ),

                    dbc.CardBody(
                        children=[

                            html.Div(
                                id=ID.CLUSTER_LEGEND,
                                className="p-2",
                                style={"minHeight": "400px", "height": "100%"}
                            )

                        ])
                ]),
        ])