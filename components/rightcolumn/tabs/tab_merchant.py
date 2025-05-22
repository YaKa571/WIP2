import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc

from backend.data_setup.tabs import tab_merchant_data_setup
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import Icons, IconID

COLOR_BLUE_MAIN = "#0d6efd"


# Info: Edit grid layout in assets/css/tabs.css

# TODO: Free...(Yannic): Idee untere Teil der Seite wie in Skizze, oben Verteilung der Händlerkategorien und
# Aufschlüsselung (evtl. als Popup)
def create_merchant_content():
    return html.Div(
        className="tab-content-inner merchant-tab",
        children=[

            _create_merchant_heading(),
            # top: general data
            create_merchant_kpi(),
            # bottom: individual merchant data
            create_merchant_graph()

        ])


def _create_merchant_heading() -> html.Div:
    """
    Creates and returns a `html.Div` element specifically styled for a merchant section
    heading in a user interface. The returned `html.Div` includes a dummy paragraph
    element, a heading with the text "Merchant", an info icon, and a tooltip describing
    the info icon.

    Returns:
        html.Div: A Div element containing the merchant section heading and supplementary UI
        elements.
    """
    return html.Div(
        className="tab-heading-wrapper",
        children=[

            html.P(),  # Dummy element
            html.H4("Merchant", id=ID.MERCHANT_HEADING),
            comp_factory.create_info_icon(ID.MERCHANT_INFO_ICON),
            dbc.Tooltip(
                target=ID.MERCHANT_INFO_ICON,
                is_open=False,
                placement="bottom-end",
                children=[
                    "Placeholder for",
                    html.Br(),
                    "the tooltip",
                    html.Br(),
                    "..."
                ])

        ])


def create_merchant_kpi():
    return dbc.Row([
        html.P("general merchant data"),
#        create_merchant_group_distribution_pie_chart(),
       create_merchant_kpis()
    ])


def create_merchant_graph():
    return dbc.Row([
        html.P("individual merchant data"),
        # searchbar for Merchant ID
        html.Div(
            [
                html.Img(src=Icons.get_icon(IconID.LENS_SEARCH), className="search-icon"),
                dcc.Input(
                    id=ID.MERCHANT_CHART_SEARCH,
                    type='text',
                    placeholder='Search by Merchant ID',
                    className='search-input',
                )
            ],
            className="search-wrapper p-2 flex-grow-1 me-2"
        ),
    ])

def create_merchant_group_distribution_pie_chart():
    """
        Creates a Dash HTML Div containing a pie chart that visualizes the distribution
        of merchant groups based on transaction counts.

        The pie chart displays merchant groups whose transaction counts meet or exceed
        a threshold (hardcoded as 1000 in this function). Smaller groups are grouped
        together into an "Other" category by the underlying data function.

        The pie chart shows both the percentage and merchant group label on each slice,
        and the chart legend is hidden for cleaner visualization.

        Returns:
            html.Div: A Dash HTML Div component containing the pie chart wrapped in a
                      flexbox container for centered display.
        """
    my_pie_df = tab_merchant_data_setup.get_merchant_group_overview(1000)

    my_pie_fig = px.pie(
        my_pie_df,
        names='merchant_group',
        values='transaction_count',
        title="Merchant Group Distribution"
    )

    my_pie_fig.update_traces(textinfo='percent+label')
    my_pie_fig.update_layout(showlegend=False)

    return html.Div(
        className="flex-wrapper",
        style={"display": "flex", "justifyContent": "center", "alignItems": "center", "height": "450px"},
        children=[
            dcc.Graph(
                id=ID.MERCHANT_PIE_CHART_DISTRIBUTION,
                figure=my_pie_fig,
                config={"displayModeBar": True, "displaylogo": False},
                style={"width": "400px", "height": "400px"}
            )
        ]
    )

def create_merchant_kpis():
    """
       Creates a Dash HTML Div containing two KPI cards related to merchant groups.

       KPI 1: Displays the most frequently used merchant group and its transaction count.
       KPI 2: Displays the merchant group with the highest total transfer value and the value.

       Each KPI card includes an icon, a descriptive title, and values wrapped in loading
       components for asynchronous data updates.

       Returns:
           html.Div: A Dash HTML Div component containing two KPI cards laid out in a flexbox.
       """
    group_1, count_1 = tab_merchant_data_setup.get_most_frequently_used_merchant_group()
    count_1 = str(count_1) + " Transactions"
    group_2, value_2 = tab_merchant_data_setup.get_highest_value_merchant_group()
    value_2 = "$" + str(value_2)
    return html.Div(children=[
        html.Div(children=[
            # KPI 1: Most frequently used merchant group
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.REPEAT, cls="icon icon-small"),
                    html.P("Most frequently used merchant group", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(group_1, className="kpi-card-value"),
                            html.P(count_1, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_MOST_FREQUENTLY_MERCHANT_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
            # KPI 2: Merchant group with the highest total transfers
            dbc.Card(children=[
                dbc.CardHeader(children=[
                    comp_factory.create_icon(IconID.USER_PAYING, cls="icon icon-small"),
                    html.P("Merchant group with the highest total transfers", className="kpi-card-title")

                ],
                    className="card-header"
                ),

                dbc.CardBody(children=[

                    dcc.Loading(children=[
                        html.Div(children=[
                            html.P(group_2, className="kpi-card-value"),
                            html.P(value_2, className="kpi-card-value kpi-number-value")
                        ],
                            id=ID.MERCHANT_KPI_HIGHEST_VALUE_MERCHANT_GROUP
                        )
                    ],
                        type="circle",
                        color=COLOR_BLUE_MAIN)

                ],
                    className="card-body",
                )
            ],
                className="card kpi-card",
            ),
        ],
            className="flex-wrapper"
        )
    ])
