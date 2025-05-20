import dash_bootstrap_components as dbc
from dash import html, dcc

from components.factories import component_factory as comp_factory
from frontend.component_ids import ID

"""
appearance of tab cluster
"""


# Info: Edit grid layout in assets/css/tabs.css


# TODO: @Yannic
# TODO: Darkmode
def create_cluster_content():
    return html.Div(
        children=[

            _create_heading(),
            # TODO Names
            dcc.Dropdown(['Default', 'Age Group', 'Income vs Expenditures', 'Test'], 'Default',
                         id=ID.CLUSTER_DROPDOWN),
            html.Hr(),
            html.Div(
                dcc.RadioItems(
                    id=ID.CLUSTER_DEFAULT_SWITCH,
                    options=[
                        {'label': 'Total Value', 'value': 'total_value'},
                        {'label': 'Average Value', 'value': 'average_value'},
                    ],
                    value='total_value'
                ),
                id=ID.CLUSTER_DEFAULT_SWITCH_CONTAINER,
                style={'display': 'none'}
            ),
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id=ID.CLUSTER_GRAPH,
                        style={"height": "100%", "minHeight": "500px", "width": "100%"}
                    ),
                    width=8
                ),
                dbc.Col(
                    html.Div(id=ID.CLUSTER_LEGEND),
                    width=4
                )
            ])
        ],
        className="tab-content-inner cluster-tab"
    )


def _create_heading() -> html.Div:
    """
    Creates a heading component for the cluster tab.

    This function generates a Dash HTML division (Div) component to be used as
    a heading section for the cluster tab. It includes a dummy placeholder
    paragraph for spacing, a heading, an information icon, and a tooltip
    providing instructions for interacting with the dropdown.

    Returns:
        html.Div: A Dash Div component that contains the heading,
        information icon, and tooltip.

    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element
            html.H4("Cluster", id=ID.CLUSTER_HEADING),
            comp_factory.create_info_icon(ID.CLUSTER_INFO_ICON),
            dbc.Tooltip(
                target=ID.CLUSTER_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Click on dropdown",
                    html.Br(),
                    "to choose Cluster"
                ])

        ])
