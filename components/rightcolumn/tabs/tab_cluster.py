from dash import html, dcc
from frontend.component_ids import IDs

# TODO: @Yannic

def create_cluster_content():
    return html.Div(
        [
            html.H1("Cluster"),
            html.P("This is the cluster page of the application."),
            # TODO Names
            dcc.Dropdown(['Default','Age Group','Income vs Expenditure'],'Default',id=IDs.CLUSTER_DROPDOWN),
            html.Hr(),
            html.Div(id=IDs.CLUSTER_DROPDOWN_OUTPUT)
        ],
        className="tab-content-wrapper flex-fill"
    )

