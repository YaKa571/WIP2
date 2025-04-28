import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from styles import Style, STYLES

if __name__ == "__main__":
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container(
        dbc.Card(
            dbc.CardBody([

                html.H5("Small Styles Example", className="card-title mb-2"),
                html.Hr(),

                dbc.Row([

                    dbc.Col(
                        dcc.Dropdown(
                            placeholder="Dropdown in a Card",
                            style=STYLES[Style.DROPDOWN]  # Pre-defined Dropdown-Style
                        ),
                        width=3
                    ),

                    dbc.Col(
                        dbc.Button(
                            "Click me",
                            className="btn btn-primary w-100",
                            style=STYLES[Style.BUTTON]  # Pre-defined Button-Style
                        ),
                        width=3
                    )

                ], className="gx-3"),

            ]),
            className="col-6 mt-3",
            style=STYLES[Style.CARD] | {"height": "400px", "backgroundColor": "#EBEBEB"}   # Pre-defined Card-Style
                                                                                           # + individual properties
        ),
        fluid=True
    )

    app.run(debug=True)
