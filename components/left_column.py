from typing import TypedDict, Callable, Any, Dict

import dash_bootstrap_components as dbc
from dash import html

import components.component_factory as comp_factory
from backend.data_manager import DataManager
from frontend.component_ids import IDs
from frontend.icon_manager import Icons, IconID


# Define a TypedDict for KPI configuration
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
KPI_CONFIG: Dict[IDs, KPIConfig] = {
    IDs.KPI_CARD_AMT_TRANSACTIONS: KPIConfig(
        title="Transactions",
        icon=IconID.CHART_PIPE,
        value_fn=lambda dm: dm.amount_of_transactions,
        format_fn=lambda v: f"{v:,}".replace(",", "."),
    ),
    IDs.KPI_CARD_SUM_OF_TRANSACTIONS: KPIConfig(
        title="Total Value",
        icon=IconID.MONEY_DOLLAR,
        value_fn=lambda dm: dm.sum_of_transactions,
        format_fn=lambda v: f"${v:,.2f}",
    ),
    IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT: KPIConfig(
        title="Avg. Transaction",
        icon=IconID.CHART_AVERAGE,
        value_fn=lambda dm: dm.avg_transaction_amount,
        format_fn=lambda v: f"${v:,.2f}",
    ),
}


def create_kpi_card(card_id: IDs, data_manager: DataManager) -> dbc.Card:
    """
    Creates and returns a KPI card component with specific properties including
    value, icon, and title. The configuration for the KPI card is sourced based
    on the provided card ID.

    Raises:
        ValueError: If no KPI configuration is found for the given card ID.

    Args:
        card_id (IDs): Identifier for the KPI card to retrieve the configuration.
        data_manager (DataManager): Data manager instance used to calculate the KPI
            value.

    Returns:
        dbc.Card: A Dash Bootstrap Component representing the KPI card.
    """
    config = KPI_CONFIG.get(card_id)
    if config is None:
        raise ValueError(f"No KPI configuration found for {card_id}")

    raw_value = config["value_fn"](data_manager)
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


def create_kpi_cards(data_manager: DataManager) -> html.Div:
    """
    Creates a collection of KPI cards in a dashboard layout.

    This function generates a set of KPI cards based on the configuration
    defined in `KPI_CONFIG`. Each card is created dynamically using the
    `create_kpi_card` function with the provided `data_manager` instance. The
    resulting cards are wrapped in a `html.Div` container with a specific
    CSS class for styling.

    Args:
        data_manager: An instance of the DataManager object used to provide
            data required for generating the KPI cards.

    Returns:
        A Div component containing all the dynamically created KPI cards.
    """
    cards = [
        create_kpi_card(kpi_id, data_manager)
        for kpi_id in KPI_CONFIG
    ]
    return html.Div(cards, className="top-cards")


def create_map_card(data_manager: DataManager) -> dbc.Card:
    """
    Creates and returns a styled Dash Bootstrap Card containing a placeholder text
    for a map. This card serves as a visual placeholder that can be extended to
    display dynamic map-related content later.

    Return:
        dbc.Card: A Dash Bootstrap Card object with a placeholder content for a map.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H3("Map", className="card-title text-center"),

                html.Div(
                    comp_factory.create_usa_map(data_manager),
                    className="map-container flex-fill"
                )
            ],
            className="map-card-body d-flex flex-column",
        ),
        className="bottom-card card h-100"
    )


def create_left_column(data_manager: DataManager) -> html.Div:
    """
    Creates the left column of a dashboard layout.

    The left column includes KPI cards and a map card generated dynamically
    based on the provided data manager.

    Parameters:
        data_manager (DataManager): The data source manager used to retrieve
            and process data for populating KPI cards and the map card.

    Returns:
        dash.html.Div: A Div element containing the left column layout structure
            with KPI cards and a map card.
    """
    return html.Div(
        [
            create_kpi_cards(data_manager),
            create_map_card(data_manager),
        ],
        className="left-column",
    )
