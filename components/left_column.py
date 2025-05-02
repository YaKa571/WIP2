from typing import TypedDict, Callable, Any, Dict

import dash_bootstrap_components as dbc
from dash import html

import components.component_factory as comp_factory
from backend.data_manager import DataManager
from frontend.component_ids import IDs
from frontend.icon_manager import Icons, IconID
from frontend.styles import STYLES, Style


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
        value_fn=lambda dm: len(dm.df_transactions),
        format_fn=lambda v: f"{v:,}".replace(",", "."),
    ),
    IDs.KPI_CARD_SUM_OF_TRANSACTIONS: KPIConfig(
        title="Total Value",
        icon=IconID.MONEY_DOLLAR,
        value_fn=lambda dm: dm.df_transactions["amount"].sum(),
        format_fn=lambda v: f"${v:,.2f}",
    ),
    IDs.KPI_CARD_AVG_TRANSACTION_AMOUNT: KPIConfig(
        title="Avg. Transaction",
        icon=IconID.CHART_AVERAGE,
        value_fn=lambda dm: dm.df_transactions["amount"].mean(),
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
        className="kpi-card-icon"
    )

    return dbc.Card(
        dbc.CardBody([
            icon,
            html.P(value_str, className="card-value mb-0 pb-0"),
            html.P(config["title"], className="card-title m-0 p-0"),
        ], style=STYLES[Style.KPI_CARD_BODY]),
        style=STYLES[Style.KPI_CARD],
        id=str(card_id.value),
        className="w-100 kpi-card"
    )


def create_kpi_cards(data_manager: DataManager) -> dbc.Row:
    """
    Creates and returns a layout row containing KPI cards.

    This function generates a dashboard row with cards for each KPI defined in the global
    KPI configuration. The data for each KPI is managed and passed through the provided
    data manager instance. The returned row consists of multiple responsive columns where
    each column contains a single KPI card.

    Args:
        data_manager (DataManager): The data manager instance used to fetch or manage KPI
        data.

    Returns:
        dbc.Row: A Bootstrap row populated with KPI cards, each wrapped in a responsive
        column.
    """
    cols = [
        dbc.Col(create_kpi_card(kpi_id, data_manager), md=4)
        for kpi_id in KPI_CONFIG
    ]
    return dbc.Row(cols, className="gx-3 mb-3 kpi-cards-row")


def create_map_card(data_manager: DataManager) -> dbc.Card:
    """
    Creates and returns a styled Dash Bootstrap Card containing a placeholder text
    for a map. This card serves as a visual placeholder that can be extended to
    display dynamic map-related content later.

    Return:
        dbc.Card: A Dash Bootstrap Card object with a placeholder content for a map.
    """
    return dbc.Card(
        dbc.CardBody([

            html.H3("Map", className="card-title text-center"),

            html.Div(
                comp_factory.create_usa_map(data_manager),
                className="d-flex flex-fill",
                style={"minHeight": 0, "borderRadius": "19px"}
            )],
            className="d-flex flex-column flex-fill",
            style={"minHeight": 0, "borderRadius": "19px"}
        ),
        className="d-flex flex-column",
        style=STYLES[Style.CARD] | {"height": "100%"}
    )


def create_left_column(data_manager: DataManager) -> dbc.Col:
    """
    Creates the left column layout for a dashboard, which includes key performance
    indicator (KPI) cards and a map card. This function uses components from
    Dash Bootstrap Components (dbc) to construct the column layout.

    Args:
        data_manager (DataManager): An object that manages and provides data required
        for creating the KPI cards.

    Returns:
        dbc.Col: A Dash Bootstrap Component column object containing the KPI cards
        and map card with a specified width and a flex column layout.
    """
    return dbc.Col(
        [
            create_kpi_cards(data_manager),
            create_map_card(data_manager),
        ],
        width=6,
        className="d-flex flex-column"
    )
