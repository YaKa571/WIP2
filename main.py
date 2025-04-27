import dash_bootstrap_components as dbc
from dash import Dash, html

from components.left_column import create_left_column
from components.right_column import create_right_column
from frontend.styles import STYLES, Style


def create_app():
    external_style = [dbc.themes.BOOTSTRAP]
    app = Dash(__name__, external_stylesheets=external_style)

    app.layout = dbc.Container(
        [
            # Row with Title
            dbc.Row(
                dbc.Col(
                    html.H1(
                        "Financial Transactions Dashboard",
                        className="text-center m-0 pb-3",
                        style=STYLES[Style.APP_TITLE]
                    )
                )
            ),

            # Row with Left and Right Column
            dbc.Row(
                [
                    create_left_column(),
                    create_right_column()
                ],
                className="gx-3",
                style={"height": "calc(100vh - 6rem)"}
            )
        ],
        fluid=True,
        className="p-3 m-0",
        style=STYLES[Style.BODY]
    )

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
