import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html, dcc
from plotly.graph_objs._figure import Figure

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm: DataManager = DataManager.get_instance()
PIE_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False
}
COLOR_BLUE_MAIN = "#0d6efd"


# TODO: @Diego
def create_home_content() -> html.Div:
    return html.Div(children=[

        _create_top_kpis(),
        _create_middle_circle_diagrams()
    ],
        className="tab-content-inner"
    )


def create_pie_graph(data: dict, colors=None, textinfo: str = "percent+label", showlegend: bool = True,
                     dark_mode: bool = False) -> go.Figure:
    if colors is None:
        colors = ["#c65ed4", "#5d9cf8"]  # Female = pink, Male = blue

    textcolor = "white" if dark_mode else "black"

    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(
        data=[go.Pie(
            name="",
            labels=labels,
            values=values,
            hole=0.42,
            marker=dict(colors=colors),
            textinfo=textinfo,
            textfont=dict(color=textcolor),
            hovertemplate="%{label}<br>%{percent}<br>$%{value:,.2f}"
        )],
        layout=go.Layout(
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=showlegend
        )
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            x=1,  # 100% right
            y=1,  # 100% top
            xanchor="right",
            yanchor="top",
            font=dict(size=12, color="#0d6efd", weight="bold")
        )
    )

    return fig


def _create_top_kpis() -> html.Div:
    """
    Creates a section of top key performance indicators (KPIs) in the form of cards.

    Each KPI card is represented using `dbc.Card` and organized into the following
    categories:
    1. Highest Value Merchant
    2. Most Frequent Merchant
    3. Highest Value User
    4. Most Frequent User

    Each card contains a header with the respective KPI label and a body displaying the
    KPI value.

    Returns:
        html.Div: A `Div` container element that wraps all the KPI cards with a
        specific class style for layout and styling consistency.
    """
    return html.Div(children=[

        # KPI 1: Highest Value Merchant
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.TROPHY, cls="icon icon-small"),
                html.P("Most Valuable Merchant", className="kpi-card-title")

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P(
                    f"{dm.home_kpi.most_valuable_merchant.mcc_desc}",
                    className="kpi-card-value"),
                html.P(f"${dm.home_kpi.most_valuable_merchant.value}",
                       className="kpi-card-value kpi-number-value")

            ],
                className="card-body",
                id=ID.HOME_KPI_MOST_VALUABLE_MERCHANT

            )],
            className="card kpi-card",
        ),

        # KPI 2: Most Frequent Merchant
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                html.P("Most Visited Merchant", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P(
                    f"{dm.home_kpi.most_visited_merchant.mcc_desc}",
                    className="kpi-card-value"),
                html.P(f"{dm.home_kpi.most_visited_merchant.visits} visits",
                       className="kpi-card-value kpi-number-value")

            ],
                className="card-body",
                id=ID.HOME_KPI_MOST_VISITED_MERCHANT

            )],
            className="card kpi-card",
        ),

        # KPI 3: Highest Value User
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                html.P(children="Top Spending User", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P(
                    f"{dm.home_kpi.top_spending_user.gender}, {dm.home_kpi.top_spending_user.current_age} years",
                    className="kpi-card-value"),
                html.P(f"${dm.home_kpi.top_spending_user.value}",
                       className="kpi-card-value kpi-number-value")

            ],
                className="card-body",
                id=ID.HOME_KPI_TOP_SPENDING_USER

            )],
            className="card kpi-card",
        ),

        # KPI 4: Peak Hour
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.TIME, cls="icon icon-small"),
                html.P(children="Peak Hour", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P(f"{dm.home_kpi.peak_hour.hour_range}", className="kpi-card-value"),
                html.P(f"{dm.home_kpi.peak_hour.value} transactions", className="kpi-card-value kpi-number-value")

            ],
                className="card-body",
                id=ID.HOME_KPI_MOST_FREQUENT_USER

            )],
            className="card kpi-card",
        ),

    ],
        className="flex-wrapper"
    )


def _create_middle_circle_diagrams() -> html.Div:
    """
    Creates a component containing visual representations of expenditures by gender and
    expenditures by channel using pie chart graphs. The method returns a layout structure
    that is wrapped within an HTML `Div`.

    Returns:
        html.Div: A Div component containing two cards; each card includes
        a header and a body. The headers contain icons and titles, and the
        bodies include pie chart graphs for gender-based and channel-based
        expenditure data.
    """
    return html.Div(children=[

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.GENDERS, cls="icon icon-small"),
                html.P(children="Expenditures by Gender", className="graph-card-title"),

            ],
                className="card-header"),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_GENDER,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )

                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)
            ])

        ],
            className="card graph-card"),

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.CART, cls="icon icon-small"),
                html.P(children="Expenditures by Channel", className="graph-card-title"),

            ],
                className="card-header"),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_CHANNEL,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )

                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)
            ])

        ],
            className="card graph-card"),

        dbc.Card(children=[

            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.CAKE, cls="icon icon-small"),
                html.P(children="Expenditures by Age", className="graph-card-title"),

            ],
                className="card-header"
            ),

            dbc.CardBody(children=[
                dcc.Loading(children=[
                    dcc.Graph(
                        figure=Figure(),
                        className="circle-diagram",
                        id=ID.HOME_GRAPH_EXPENDITURES_BY_AGE,
                        responsive=True,
                        config=PIE_CONFIG,
                        style={"height": "16vh", "minHeight": 0, "minWidth": 0}
                    )
                ],
                    type="circle",
                    color=COLOR_BLUE_MAIN)

            ])

        ],
            className="card graph-card"),

    ],
        className="flex-wrapper"
    )
