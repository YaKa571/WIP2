from dash import html


# TODO: Free...
def create_merchant_content():
    return html.Div(
        [
            html.H1("Merchant"),
            html.P("This is the merchant page of the application."),
        ],
        className="tab-content-inner"
    )