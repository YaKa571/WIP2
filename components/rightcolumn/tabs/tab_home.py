from dash import html

# TODO: @Diego
def create_home_content():
    return html.Div(
        [
            html.H1("Home"),
            html.P("This is the home page of the application."),
        ],
        className="tab-content-wrapper flex-fill"
    )