import dash_bootstrap_components as dbc
from dash import html, dcc

from backend.callbacks.tabs import tab_cluster_callbacks
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID


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

            _create_heading(),
            _create_button_row(),
            _create_cluster_age_group_switch(),
            _create_cluster_control_merchant_group(),
            _create_cluster_legend(),
            _create_cluster_visualization()

        ]
    )


def _create_heading() -> html.Div:
    """
    Creates a heading section for the cluster analysis tab.

    This function generates a Dash HTML Division (html.Div) component that serves as
    the heading section for the cluster analysis feature in a web application. The heading
    includes a button to toggle views, a title, an informational icon, and a tooltip that
    provides detailed instructions on using the cluster analysis functionalities. The layout
    and style are defined using predefined classes and IDs.

    Returns:
        html.Div: A Dash HTML Div element containing the cluster analysis tab heading,
        including all its child components.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.Button(
                className="settings-button-text hidden",
                id=ID.CLUSTER_BTN_MAP,
                children=[

                    html.I(className="bi bi-globe-americas me-2"),
                    "Show all States"

                ]),
            html.H4("Cluster Analysis", id=ID.CLUSTER_HEADING, className="green-text"),
            comp_factory.create_info_icon(ID.CLUSTER_INFO_ICON),
            dbc.Tooltip(
                target=ID.CLUSTER_INFO_ICON,
                is_open=False,
                placement="bottom-end",
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


def _create_button_row():
    """
    Creates a row of buttons for UI interaction.

    The function returns a layout element consisting of a row of buttons. Each button
    is associated with specific functionality to display financial data based on user
    selection. Each button includes an associated icon and label.

    Returns:
        Div: A Dash Div component containing a row of buttons with specific options.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            html.Button(
                className="settings-button-text option-btn",
                id=ID.CLUSTER_BTN_TOTAL_VALUE,
                children=[

                    html.I(className="bi bi-cash-stack me-2"),
                    "Total Value"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.CLUSTER_BTN_AVERAGE_VALUE,
                children=[

                    html.I(className="bi bi-calculator-fill me-2"),
                    "Average Value"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.CLUSTER_BTN_INC_VS_EXP,
                children=[

                    html.I(className="bi bi-bank me-2"),
                    "Income vs. Expenses"

                ]),

        ])


def _create_cluster_age_group_switch():
    """
        Creates a UI component with buttons to toggle between viewing
        data for all ages or segmented by age groups.

        Returns:
            html.Div: A Div containing the age group toggle buttons.
        """
    return html.Div(
        className="flex-wrapper",
        children=[

            html.Button(
                className="settings-button-text option-btn",
                id=ID.CLUSTER_BTN_ALL_AGES,
                children=[

                    html.I(className="bi bi-people-fill me-2"),
                    "All Ages"

                ]),

            html.Button(
                className="settings-button-text option-btn",
                id=ID.CLUSTER_BTN_AGE_GROUP,
                children=[

                    html.I(className="bi bi-balloon-fill me-2"),
                    "Age Groups"

                ])

        ])


def _create_cluster_control_merchant_group():
    """
        Creates the container Div that holds the merchant group filter dropdown.
        This allows filtering cluster data by merchant groups.

        Returns:
            html.Div: The container for merchant group dropdown control.
        """
    return html.Div(
        className="flex-wrapper",
        children=[

            html.Div(
                className="flex-wrapper",
                children=[tab_cluster_callbacks.get_cluster_merchant_group_input()],
                id=ID.CLUSTER_CONTROL_MERCHANT_GROUP_DROPDOWN,
                style={"display": "flex", "width": "100%"}
            )

        ]
    )


def _create_cluster_legend():
    """
    Creates a cluster legend component.

    This function generates a user interface component for displaying a cluster legend.
    It consists of a collapsible card containing the legend title, an icon, and a toggle
    button for expanding or collapsing the legend content.

    Returns:
        dash.html.Div: A Div component containing the cluster legend UI.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            dbc.Card(
                className="graph-card",
                children=[
                    dbc.CardHeader(
                        style={"position": "relative"},
                        children=[

                            html.Div(
                                className="card-header-inline-wrapper",
                                children=[

                                    comp_factory.create_icon(IconID.LEGEND, cls="icon icon-xs"),
                                    html.P("Cluster Legend", className="graph-card-title"),

                                ]
                            ),

                            dbc.Button(
                                html.I(className="fa fa-chevron-up"),
                                id=ID.CLUSTER_BTN_TOGGLE_LEGEND,
                                n_clicks=0,
                                className="legend-btn",
                            )

                        ]
                    ),
                    dbc.Collapse(
                        id=ID.CLUSTER_COLLAPSE_LEGEND,
                        is_open=True,
                        children=dbc.CardBody(
                            html.Div(
                                id=ID.CLUSTER_LEGEND,
                                className="legend-item-container"
                            )
                        ),
                    )
                ]
            )
        ])


def _create_cluster_visualization():
    """
        Creates the visualization layout for the cluster tab including two cards:
        one for the cluster scatter plot graph and one for the cluster legend.

        Returns:
            html.Div: The visualization container with graph and legend cards.
        """
    return html.Div(
        className="flex-wrapper",
        children=[

            dbc.Card(
                className="graph-card with-bar-chart lower-modebar",
                children=[

                    dbc.CardHeader(
                        children=[

                            html.Div(
                                className="card-header-inline-wrapper",
                                children=[

                                    comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-xs"),
                                    html.P("Cluster Visualization", className="graph-card-title"),

                                ]
                            )
                        ]
                    ),

                    dbc.CardBody(
                        children=[

                            dcc.Graph(
                                figure=comp_factory.create_empty_figure(),
                                id=ID.CLUSTER_GRAPH,
                                className="bar-chart",
                                config={
                                    "scrollZoom": True,
                                    "displayModeBar": True,
                                    "displaylogo": False
                                },
                                responsive=True,
                                style={
                                    "height": "100%",
                                    "width": "100%",
                                    "minHeight": 0,
                                    "minWidth": 0}
                            )

                        ]
                    )
                ]
            ),

        ])
