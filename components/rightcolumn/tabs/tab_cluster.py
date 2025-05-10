from dash import html, dcc

# TODO: @Yannic

def create_cluster_content():
    return html.Div(
        [
            html.H1("Cluster"),
            html.P("This is the cluster page of the application."),
            # TODO Names
            dcc.Dropdown(['Default','Age Group','Income vs Expenditure'],'Default',id='cluster-dropdown'),
        ],
        className="tab-content-wrapper flex-fill"
    )