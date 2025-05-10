from dash import html


# TODO: Free...
def create_fraud_content():
    return html.Div(
        [
            html.H1("Fraud"),
            html.P("This is the fraud page of the application."),
        ],
        className="tab-content-wrapper flex-fill"
    )
