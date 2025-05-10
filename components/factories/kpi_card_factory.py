# Define a TypedDict for KPI configuration
from typing import TypedDict, Callable, Any, Dict

import dash_bootstrap_components as dbc
from dash import html

from backend.data_manager import DataManager
from frontend.component_ids import ID
from frontend.icon_manager import IconID, Icons


class KPIConfig(TypedDict):
    """
    Represents a TypedDict for configuration of a KPI.

    KPIConfig defines the structure for configuring KPI data, including its title,
    icon representation, value computation function, and formatting function.
    It is used to organize and manage KPI-related configurations in a structured way.
    """
    title: str
    icon: IconID
    value_fn: Callable[[DataManager], Any]
    format_fn: Callable[[Any], str]


# Mapping of KPI IDs to their configuration
# Add new KPI Cards here. They need an Icon and an ID
KPI_CONFIG: Dict[ID, KPIConfig] = {
    ID.KPI_CARD_AMT_TRANSACTIONS: KPIConfig(
        title="Transactions",
        icon=IconID.CHART_PIPE,
        value_fn=lambda dm: dm.amount_of_transactions,
        format_fn=lambda v: f"{v:,}".replace(",", "."),
    ),
    ID.KPI_CARD_SUM_OF_TRANSACTIONS: KPIConfig(
        title="Total Value",
        icon=IconID.MONEY_DOLLAR,
        value_fn=lambda dm: dm.sum_of_transactions,
        format_fn=lambda v: f"${v:,.2f}",
    ),
    ID.KPI_CARD_AVG_TRANSACTION_AMOUNT: KPIConfig(
        title="Avg. Transaction",
        icon=IconID.CHART_AVERAGE,
        value_fn=lambda dm: dm.avg_transaction_amount,
        format_fn=lambda v: f"${v:,.2f}",
    ),
}


def create_kpi_card(card_id: ID) -> dbc.Card:
    """
    Creates and returns a KPI card component with specific properties including
    value, icon, and title. The configuration for the KPI card is sourced based
    on the provided card ID.

    Raises:
        ValueError: If no KPI configuration is found for the given card ID.

    Args:
        card_id (ID): Identifier for the KPI card to retrieve the configuration.

    Returns:
        dbc.Card: A Dash Bootstrap Component representing the KPI card.
    """
    config = KPI_CONFIG.get(card_id)
    if config is None:
        raise ValueError(f"No KPI configuration found for {card_id}")

    raw_value = config["value_fn"](DataManager.get_instance())
    value_str = config["format_fn"](raw_value)
    icon = html.Img(
        src=Icons.get_icon(config["icon"]),
        className="kpi-card-icon",
        draggable="false"
    )

    return dbc.Card(
        dbc.CardBody([
            icon,
            html.P(value_str, className="kpi-card-value mb-0 pb-0"),
            html.P(config["title"], className="kpi-card-title m-0 p-0"),
        ],
            className="d-flex flex-column justify-content-center align-items-center"
        ),
        id=str(card_id.value),
        className="card"
    )
