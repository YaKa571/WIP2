from dash import html

# TODO: @Son
def create_user_content():
    return html.Div(
        [
            html.H1("User"),
            html.P("This is the user page of the application."),
        ],
        className="tab-content-wrapper flex-fill"
    )