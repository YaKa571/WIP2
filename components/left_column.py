import dash_bootstrap_components as dbc
from dash import html

from backend.data_manager import data_frame_transactions as transactions
from frontend.component_ids import IDs
from frontend.icon_manager import Icons, IconID
from frontend.styles import STYLES, Style


def create_kpi_card(card_id: IDs, card_title: str = ""):
    amt_transactions_str = f"{len(transactions):,}".replace(",", ".")
    sum_transactions_str = f"${transactions['amount'].sum():,.2f}"
    mean_transactions_str = f"${transactions['amount'].mean():,.2f}"

    if card_id == IDs.KPI_CARD_AMT_TRANSACTIONS:
        icon = html.Img(src=Icons.get_icon(IconID.CHART_PIPE), style=STYLES[Style.ICON])
        inner = html.P(amt_transactions_str, className="card-value mb-0 pb-0")

    elif card_id == IDs.KPI_CARD_SUM_OF_TRANSACTIONS:
        icon = html.Img(src=Icons.get_icon(IconID.MONEY_DOLLAR), style=STYLES[Style.ICON])
        inner = html.P(sum_transactions_str, className="card-value mb-0 pb-0")
    elif card_id == IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT:
        icon = html.Img(src=Icons.get_icon(IconID.CHART_AVERAGE), style=STYLES[Style.ICON])
        inner = html.P(mean_transactions_str, className="card-value mb-0 pb-0")
    else:
        icon = None
        inner = html.P("Unsupported card_id", className="card-value mb-0 pb-0")

    return dbc.Card(
        dbc.CardBody([
            icon,
            inner,
            html.P(card_title, className="card-title fw-bold fs-5")
        ],
            style=STYLES[Style.KPI_CARD_BODY]),
        style=STYLES[Style.KPI_CARD],
        id=str(card_id.value),  # Enum value is used as ID
        className="w-100 kpi-card"
    )


def create_kpi_cards():
    return dbc.Row(
        [
            # Separate column for each KPI card
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AMT_TRANSACTIONS, "Transactions"),
                md=4
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_SUM_OF_TRANSACTIONS, "Total Value"),
                md=4
            ),
            dbc.Col(
                create_kpi_card(IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT, "Avg. Transaction"),
                md=4
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
