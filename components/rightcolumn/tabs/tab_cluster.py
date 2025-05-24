import dash_bootstrap_components as dbc
from dash import html, dcc

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID
from components.constants import COLOR_BLUE_MAIN


# TODO: Dark-Mode for the Graph, style Radio-Buttons

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

            _create_heading(),
            _create_cluster_controls(),
            _create_cluster_visualization()

        ]
    )


def _create_heading() -> html.Div:
    """
    Creates a heading component for the cluster analysis tab.

    This function generates a styled HTML division containing a heading
    title, an information icon, and an associated tooltip. The tooltip
    provides additional information about selecting a cluster type and
    its significance in data visualization.

    Returns:
        html.Div: A dash HTML division containing the heading with an
        information icon and a tooltip.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element
            html.H4("Cluster Analysis", id=ID.CLUSTER_HEADING),
            comp_factory.create_info_icon(ID.CLUSTER_INFO_ICON),
            dbc.Tooltip(
                target=ID.CLUSTER_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                className="enhanced-tooltip",
                children=[
                    "Choose a Cluster Type from the dropdown",
                    html.Br(),
                    "to visualize different data groupings",
                    html.Br(),
                    "and patterns."
                ])
        ])


def _create_cluster_controls():
    """
    Creates and returns a Div element containing controls for cluster type selection
    and related settings. These controls enable the user to select a cluster type
    and configure additional options based on the selected type.

    Returns
    -------
    dash.html.Div
        A Div element containing dropdown and additional controls for cluster
        configuration.
    """
    return html.Div(
        className="flex-wrapper",
        children=[

            html.Div(
                className="flex-fill-vertical",
                children=[

                    html.Div(
                        className="section-title",
                        children=["Select Cluster Type"]
                    ),

                    dcc.Dropdown(
                        options=['Default', 'Age Group', 'Income vs Expenditures', 'Test'],
                        value='Default',
                        id=ID.CLUSTER_DROPDOWN,
                        className="settings-dropdown settings-text-centered",
                        clearable=False,
                        searchable=False
                    ),

                    html.Div(
                        id=ID.CLUSTER_DEFAULT_SWITCH_CONTAINER,
                        children=[

                            dcc.RadioItems(
                                id=ID.CLUSTER_DEFAULT_SWITCH,
                                value='total_value',
                                className="d-flex gap-3",
                                options=[
                                    {'label': 'Total Value', 'value': 'total_value'},
                                    {'label': 'Average Value', 'value': 'average_value'},
                                ])
                        ])
                ])
        ])


def _create_cluster_visualization():
    """
    Creates the cluster visualization layout for the user interface.

    This function generates a Dash HTML Div element containing two primary visual
    components: a cluster visualization graph and a legend. The visual layout is
    designed using Bootstrap cards with specific styles to ensure a responsive and
    intuitive user interface. The graph and legend provide insight into clustering
    data, with interactive elements to enhance the user's analytical experience.

    Returns:
        dash.html.Div: A Dash HTML Div element structured with visual components
        for cluster visualization, including a graph and a legend.

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
                                style={"height": "100%"}
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
                                className="p-2"
                            )

                        ])
                ])
        ])
