import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc, Output, Input, callback

from backend.callbacks.tabs import tab_merchant_callbacks
from backend.data_setup.tabs import tab_merchant_data_setup
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import Icons, IconID

COLOR_BLUE_MAIN = "#2563eb"

# Info: Edit grid layout in assets/css/tabs.css


def create_merchant_content():
    return html.Div(
        className="tab-content-inner merchant-tab",
        children=[

            _create_merchant_heading(),
            create_merchant_kpi(),
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
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Button('All Merchants', id=ID.MERCHANT_BTN_ALL_MERCHANTS, n_clicks=0, className='option-btn'),
                        html.Button('Merchant Group', id=ID.MERCHANT_BTN_MERCHANT_GROUP, n_clicks=0, className='option-btn'),
                        html.Button('Merchant', id=ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT, n_clicks=0, className='option-btn'),
                    ], className='button-radio-wrapper'),

                ], width = 10),
                dbc.Col([
                    html.Div(id='radio-output', style={'marginTop': '20px'}),
                ], width=1),
                dbc.Col([
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
                        ]),
                ], width = 1),
            ]),


        ])

def create_merchant_kpi():
    return html.Div(id=ID.MERCHANT_KPI_CONTAINER)


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


