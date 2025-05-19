import dash_bootstrap_components as dbc
from dash import html

from components.factories.kpi_card_factory import create_kpi_card
from frontend.component_ids import ID


def create_kpi_cards() -> html.Div:
    """
    Creates a collection of KPI cards in a dashboard layout.

    This function generates a set of KPI cards based on the configuration
    defined in `KPI_CONFIG`. Each card is created dynamically using the
    `create_kpi_card` function with the provided `data_manager` instance. The
    resulting cards are wrapped in a `html.Div` container with a specific
    CSS class for styling.

    Returns:
        A Div component containing all the dynamically created KPI cards.
    """
    cards = [
        create_kpi_card(kpi_id)
        for kpi_id in [
            ID.KPI_CARD_AMT_TRANSACTIONS,
            ID.KPI_CARD_SUM_OF_TRANSACTIONS,
            ID.KPI_CARD_AVG_TRANSACTION_AMOUNT
        ]
    ]
    return html.Div(cards, className="top-cards")


def create_map_card() -> dbc.Card:
    """
    Creates and returns a styled Dash Bootstrap Card containing a placeholder text
    for a map. This card serves as a visual placeholder that can be extended to
    display dynamic map-related content later.

    Return:
        dbc.Card: A Dash Bootstrap Card object with a placeholder content for a map.
    """
    return dbc.Card(
        className="card h-100 d-flex flex-column",
        children=[

            dbc.CardBody(
                className="map-card-body d-flex flex-column",
                children=[

                    html.Div(
                        id=ID.MAP_CONTAINER.value,
                        className="map-container fade-in"
                    ),

                    html.Div(
                        id=ID.MAP_SPINNER.value,
                        className="map-spinner"
                    )

                ])
        ])


def create_left_column() -> html.Div:
    """
    Creates the left column of a dashboard layout.

    The left column includes KPI cards and a map card generated dynamically
    based on the provided data manager.

    Returns:
        dash.html.Div: A Div element containing the left column layout structure
            with KPI cards and a map card.
    """
    return html.Div(
        className="left-column",
        children=[

            create_kpi_cards(),
            create_map_card(),
        ])
