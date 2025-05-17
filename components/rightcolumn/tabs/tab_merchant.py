from dash import html, dcc
from frontend.component_ids import ID
import dash_bootstrap_components as dbc

from frontend.icon_manager import Icons, IconID


# TODO: Free...(Yannic): Idee untere Teil der Seite wie in Skizze, oben Verteilung der Händlerkategorien und Aufschlüsselung (evtl. als Popup)
def create_merchant_content():
    return html.Div(
        [
            create_merchant_heading(),
            # top: general data
            create_merchant_general(),
            # bottom: individual merchant data
            create_merchant_individual()
        ],
        className="tab-content-inner"
    )

def create_merchant_heading():
    return html.Div(
        children=[
                dbc.Col(width=4),
                dbc.Col(html.H4("Merchant", id=ID.MERCHANT_HEADING, className="text-center"),
                        width=4),
                dbc.Col(
                    html.Div([
                        html.I(className="bi bi-info-circle-fill", id=ID.MERCHANT_INFO_ICON),
                        dbc.Tooltip(
                            children=[
                                # TODO: tooltip
                                "TODO",
                                html.Br(),
                                "Tooltip"
                            ],
                            target=ID.MERCHANT_INFO_ICON,
                            placement="bottom-end"
                        )
                    ], className="d-flex justify-content-end"),
                    width=4
                )
        ],
        # TODO: maybe custom css class
        className="tab-home-heading-wrapper"
    )

def create_merchant_general():
    return dbc.Row([
        html.P("general merchant data"),
        html.Hr()
    ])

def create_merchant_individual():
    return dbc.Row([
        html.P("individual merchant data"),
        # searchbar for Merchant ID
        html.Div(
            [
                html.Img(src=Icons.get_icon(IconID.LENS_SEARCH), className="search-icon"),
                dcc.Input(
                    id=ID.MERCHANT_ID_SEARCH,
                    type='text',
                    placeholder='Search by Merchant ID',
                    className='search-input',
                )
            ],
            className="search-wrapper p-2 flex-grow-1 me-2"
        ),
    ])


