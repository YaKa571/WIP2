import dash_bootstrap_components as dbc

from pyFiles.frontend.component_ids import IDs
from pyFiles.frontend.styles import STYLES, Style


def create_kpi_card(card_id: IDs, card_title: str = ""):
    return dbc.Card(
        dbc.CardBody(card_title),
        style=STYLES[Style.CARD] | {"height": "12.5vh"},
        id=card_id.value,  # Enum value is used as ID
        className="w-100"
    )


def create_kpi_cards():
    return dbc.Row(
        [
            # Separate column for each KPI card
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AMT_TRANSACTIONS, "Amount of Transactions"),
                width=4,
                className="d-flex text-center"
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_SUM_OF_TRANSACTIONS, "Sum of Transactions"),
                width=4,
                className="d-flex text-center"
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT, "Average Transaction Amount"),
                width=4,
                className="d-flex text-center"
            )
        ],
        className="gx-3 mb-3"
    )


def create_map_card():
    return dbc.Card(
        dbc.CardBody("Map..."),
        style=STYLES[Style.CARD],
        className="flex-fill"
    )


def create_left_column():
    return dbc.Col(
        [
            create_kpi_cards(),
            create_map_card()
        ],
        width=6,
        className="d-flex flex-column"
    )
