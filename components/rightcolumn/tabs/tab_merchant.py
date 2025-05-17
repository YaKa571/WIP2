from dash import html


# TODO: Free...(Yannic): Idee untere Teil der Seite wie in Skizze, oben Verteilung der Händlerkategorien und Aufschlüsselung (evtl. als Popup)
def create_merchant_content():
    return html.Div(
        [
            html.H1("Merchant"),
            html.P("This is the merchant page of the application."),
        ],
        className="tab-content-inner"
    )