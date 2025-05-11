from dash import html, dcc
from frontend.component_ids import ID
import dash_bootstrap_components as dbc

# TODO: @Yannic
# data.manager.getinsatnce
def create_cluster_content():
    return html.Div(
        [
            html.H1("Cluster"),
            html.P("This is the cluster page of the application."),
            # TODO Names
            dcc.Dropdown(['Default','Age Group','Income vs Expenditure'],'Default',id=ID.CLUSTER_DROPDOWN),
            html.Hr(),
            html.Div(id=ID.CLUSTER_DROPDOWN_OUTPUT),
            dbc.Row([
                dbc.Col([

                ], width=8),
                dbc.Col([

                ], width=4)
            ])
        ],
        className="tab-content-wrapper flex-fill"
    )

