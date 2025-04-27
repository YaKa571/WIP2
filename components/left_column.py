import dash_bootstrap_components as dbc

from frontend.component_ids import IDs
from frontend.styles import STYLES, Style


def create_kpi_card(card_id: IDs, card_title: str = ""):
    return dbc.Card(
        dbc.CardBody(card_title),
        style=STYLES[Style.CARD],
        id=card_id.value,  # Enum value is used as ID
        className="w-100 kpi-card"
    )


def create_kpi_cards():
    return dbc.Row(
        [
            # Separate column for each KPI card
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AMT_TRANSACTIONS, "Amount of Transactions"),
                md=4,
                className="d-flex text-center"
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_SUM_OF_TRANSACTIONS, "Sum of Transactions"),
                md=4,
                className="d-flex text-center"
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT, "Average Transaction Amount"),
                md=4,
                className="d-flex text-center"
            )
        ],
        className="gx-3 mb-3 kpi-cards-row"
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
