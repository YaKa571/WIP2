from dash import html

# TODO: @Yannic
def create_cluster_content():
    return html.Div(
        [
            html.H1("Cluster"),
            html.P("This is the cluster page of the application."),
        ],
        className="tab-content-wrapper flex-fill"
    )