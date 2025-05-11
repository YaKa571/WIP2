import dash_bootstrap_components as dbc
from dash import html

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID

dm = DataManager.get_instance()


# TODO: @Diego
def create_home_content():
    return html.Div(
        [
            _create_top_kpis()
        ],
        className="tab-content-inner"
    )


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
                html.P("Highest Value Merchant", className="kpi-card-title")

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P(dm.home_kpi["most_valuable_merchant"]["id"],
                       className="kpi-card-value"),
                html.P(
                    f"{dm.home_kpi["most_valuable_merchant"]["mcc"]} {dm.home_kpi["most_valuable_merchant"]["mcc_desc"]}",
                    className="kpi-card-value"),
                html.P(f"${dm.home_kpi["most_valuable_merchant"]["value"]}",
                       className="kpi-card-value kpi-number-value"),

            ],
                className="card-body",
                id=ID.HOME_KPI_HIGHEST_VALUE_MERCHANT

            )],
            className="card kpi-card",
        ),

        # KPI 2: Most Frequent Merchant
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                html.P("Most Frequent Merchant", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P("Placeholder", className="kpi-card-value"),

            ],
                className="card-body",
                id=ID.HOME_KPI_MOST_FREQUENT_MERCHANT

            )],
            className="card kpi-card",
        ),

        # KPI 3: Highest Value User
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.TROPHY, cls="icon icon-small"),
                html.P(children="Highest Value User", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P("Placeholder", className="kpi-card-value"),

            ],
                className="card-body",
                id=ID.HOME_KPI_HIGHEST_VALUE_USER

            )],
            className="card kpi-card",
        ),

        # KPI 4: Most Frequent User
        dbc.Card(children=[
            dbc.CardHeader(children=[

                comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                html.P(children="Most Frequent User", className="kpi-card-title"),

            ],
                className="card-header"),
            dbc.CardBody(children=[

                html.P("Placeholder", className="kpi-card-value"),

            ],
                className="card-body",
                id=ID.HOME_KPI_MOST_FREQUENT_USER

            )],
            className="card kpi-card",
        ),

    ],
        className="kpi-wrapper"
    )
