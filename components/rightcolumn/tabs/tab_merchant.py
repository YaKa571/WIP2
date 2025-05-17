from dash import html, dcc
from frontend.component_ids import ID
import dash_bootstrap_components as dbc

from frontend.icon_manager import Icons, IconID


# TODO: Free...(Yannic): Idee untere Teil der Seite wie in Skizze, oben Verteilung der Händlerkategorien und Aufschlüsselung (evtl. als Popup)
def create_merchant_content():
    return html.Div(
        [
            html.H1("Merchant"),
            html.P("This is the merchant page of the application."),
            # top: general data
            dbc.Row([
                html.P("general merchant data"),
                html.Hr()
            ]),
            # bottom: individual merchant data
            dbc.Row([
                html.P("individual merchant data"),
                # searchbar ID
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
            ]),
        ],
        className="tab-content-inner"
    )