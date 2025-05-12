from dash import html, dcc
from frontend.component_ids import ID
import dash_bootstrap_components as dbc
"""
appearance of tab cluster
"""
# TODO: @Yannic
# data.manager.getinsatnce
def create_cluster_content():
    return html.Div(
        [
            html.H1("Cluster"),
            html.P("This is the cluster page of the application."),
            # TODO Names
            dcc.Dropdown(['Default','Age Group','Income vs Expenditures','Test'],'Test',id=ID.CLUSTER_DROPDOWN),
            html.Hr(),
            html.Div(id=ID.CLUSTER_DROPDOWN_OUTPUT),
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id=ID.CLUSTER_GRAPH,
                        style={"height": "100%", "minHeight": "500px", "width": "100%"}
                    ),
                    width=8
                ),
                dbc.Col(
                    html.Div(id=ID.CLUSTER_KEY),
                    width=4
                )
            ])
        ],
        className="tab-content-inner"
    )

