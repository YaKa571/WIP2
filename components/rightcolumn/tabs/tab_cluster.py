from dash import html, dcc
from frontend.component_ids import ID
import dash_bootstrap_components as dbc
"""
appearance of tab cluster
"""
# TODO: @Yannic
# TODO: Darkmode
def create_cluster_heading():
    return html.Div(
        children=[
                dbc.Col(width=4),
                dbc.Col(html.H4("Cluster", id=ID.CLUSTER_HEADING, className="text-center"),
                        width=4),
                dbc.Col(
                    html.Div([
                        html.I(className="bi bi-info-circle-fill", id=ID.CLUSTER_INFO_ICON),
                        dbc.Tooltip(
                            children=[
                                "Click on dropdown",
                                html.Br(),
                                "to choose Cluster"
                            ],
                            target=ID.CLUSTER_INFO_ICON,
                            placement="bottom-end"
                        )
                    ], className="d-flex justify-content-end"),
                    width=4
                )
        ],
        # TODO: maybe custom css class
        className="tab-home-heading-wrapper"
    )
def create_cluster_content():
    return html.Div(
        [
            create_cluster_heading(),
            html.P("This is the cluster page of the application."),
            # TODO Names
            dcc.Dropdown(['Default','Age Group','Income vs Expenditures','Test'],'Default',id=ID.CLUSTER_DROPDOWN),
            html.Hr(),
            html.Div(id=ID.CLUSTER_DROPDOWN_OUTPUT),
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
        className="tab-content-inner"
    )

