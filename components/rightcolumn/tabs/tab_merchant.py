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
    """
        Creates the main content container for the Merchant tab.

        This includes the tab heading with option buttons, the input containers
        (dropdown and text input), the KPI display area, and the graph area.

        Returns:
            dash.html.Div: A Div containing all main components of the Merchant tab.
        """
    return html.Div(
        className="tab-content-inner merchant-tab",
        children=[

            create_merchant_heading(),
            create_merchant_input_container(),
            create_merchant_kpi(),
            create_merchant_graph()

        ])


def create_merchant_heading() -> html.Div:
    """
        Creates the header section of the Merchant tab with option buttons and an info icon.

        Includes buttons to select between "All Merchants", "Merchant Group", and "Merchant" views,
        a placeholder area for a "Button Map", and an info icon with a tooltip.

        Returns:
            dash.html.Div: A Div containing the tab heading row with buttons and info tooltip.
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

                ], width = 9),
                dbc.Col([
                    html.Div(html.P("Button Map")),
                ], width=2),
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
def create_merchant_input_container():
    """
        Creates the input section container for the Merchant tab.

        This container holds two separate input wrappers:
        - A dropdown for selecting a merchant group (initially hidden).
        - A text input for entering an individual merchant ID (initially hidden).

        Returns:
            dash.html.Div: A Div containing input containers for merchant group and individual merchant.
        """
    return html.Div(
        dbc.Row([
            dbc.Col([
                # Container for Merchant Group dropdown input
                html.Div(
                    children=[tab_merchant_callbacks.get_merchant_group_input_container()],
                    id="merchant-group-input-wrapper",
                    style={"display": "none"}  # initially hidden
                ),
                # Container for Individual Merchant ID input
                html.Div(
                    children=[tab_merchant_callbacks.get_merchant_input_container()],
                    id="merchant-input-wrapper",
                    style={"display": "none"}  # initially hidden
                ),
            ])
        ])
    )

def create_merchant_kpi():
    """
        Creates the KPI display container for the Merchant tab.

        This is a placeholder Div where dynamic KPI content will be injected via callbacks.

        Returns:
            dash.dbc.Row: A Bootstrap row containing the KPI container Div.
        """
    return dbc.Row([
        html.Div(id=ID.MERCHANT_KPI_CONTAINER)
    ])


def create_merchant_graph():
    """
    Creates a styled card container for displaying the merchant transaction graph.

    This function returns a Dash HTML Div that contains a Bootstrap card layout.
    The card includes a header with a dynamic title and an icon, and a body section
    with a Dash Graph component. The actual graph content is expected to be
    updated dynamically via a callback.

    Returns:
        dash.html.Div: A styled card layout with a placeholder for a merchant transaction graph.
    """
    return html.Div(
        className="flex-wrapper flex-fill",
        children=[
            dbc.Card(
                className="graph-card with-bar-chart",
                style={"flex": "1 1 0", "height": "100%", "minHeight": "400px"},
                children=[
                    dbc.CardHeader(
                        children=[
                            comp_factory.create_icon(IconID.CLUSTER, cls="icon icon-small"),
                            html.H3(id=ID.MERCHANT_GRAPH_TITLE, className="graph-title")
                        ]
                    ),
                    dbc.CardBody(
                        style={"height": "100%", "padding": "1rem"},
                        children=[
                            dcc.Graph(
                                id=ID.MERCHANT_GRAPH_CONTAINER,
                                className="bar-chart",
                                config={"displayModeBar": True, "displaylogo": False},
                                style={
                                    "height": "350px",  # fix height to ensure rendering
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )




