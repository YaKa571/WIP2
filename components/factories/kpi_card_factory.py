from typing import TypedDict, Callable, Any, Dict, Union

import dash_bootstrap_components as dbc
from dash import html

from backend.data_manager import DataManager
from components.factories import component_factory as comp_factory
from frontend.component_ids import ID
from frontend.icon_manager import IconID


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


def create_kpi_card_body(value: Union[int, float], comparison_value: Union[int, float],
                         format_fn: Callable[[Any], str], state: str = None, tooltip_id: ID = None) -> dbc.CardBody:
    """
    Creates a card body for a KPI card with comparison to the average value per state.

    Args:
        value: The value for the specific state or selection
        comparison_value: The average value per state for comparison
        format_fn: Function to format the value for display
        state: The selected state, if None (USA-wide) set values to 0% and =
        tooltip_id: ID for the tooltip that explains the percentage

    Returns:
        dbc.CardBody: A card body component with comparison indicators
    """
    # If state is None (USA-wide), set values to 0% and =
    if state is None:
        arrow = "="  # Equal sign
        color = "gray"
        pct_text = "0.0%"
    else:
        # Calculate percentage difference
        if comparison_value == 0:
            pct_diff = 0
        else:
            pct_diff = ((value - comparison_value) / comparison_value) * 100

        # Determine arrow direction and color
        if pct_diff > 0:
            arrow = "↑"  # Up arrow
            color = "green"
            pct_text = f"+{pct_diff:.1f}%"
        elif pct_diff < 0:
            arrow = "↓"  # Down arrow
            color = "red"
            pct_text = f"{pct_diff:.1f}%"
        else:
            arrow = "="  # Equal sign for no difference
            color = "gray"
            pct_text = "0.0%"

    # Format the comparison value for display in the tooltip
    # For transactions, always show 2 decimal places
    if isinstance(comparison_value, (int, float)):
        comparison_value_str = f"{comparison_value:,.2f}".replace(",", ".")
    else:
        comparison_value_str = format_fn(comparison_value)

    # Create the card body with the comparison indicators
    card_body_id = str(tooltip_id.value) + "-body" if tooltip_id else None
    symbol = "" if tooltip_id == ID.KPI_CARD_AMT_TRANSACTIONS_TOOLTIP else "$"

    card_body = dbc.CardBody(
        id=card_body_id,
        children=[

            html.Span(arrow, style={"color": color, "fontSize": "24px", "fontWeight": "bold"}),
            html.Span(pct_text, className="mt-1",
                      style={"color": color, "fontSize": "1.2rem", "fontWeight": "bold"}),

            dbc.Tooltip(
                id={"type": "tooltip", "id": str(tooltip_id.value)} if tooltip_id else None,
                target=card_body_id,
                placement="bottom",
                children=[

                    f"This percentage shows how this value compares ",
                    html.Span("to the average value per state.", style={"fontWeight": "bold"}),
                    html.Hr(),
                    f"Average value per state: ",
                    html.Span(f"{symbol}{comparison_value_str}", style={"fontWeight": "bold"})

                ]
            )
            if tooltip_id else []

        ]
    )

    return card_body


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

    dm = DataManager.get_instance()
    raw_value = config["value_fn"](dm)
    value_str = config["format_fn"](raw_value)
    icon = comp_factory.create_icon(config["icon"], cls="icon icon-small")

    # Get average value per state for comparison (if available)
    # For the main KPI cards, we need to calculate the average per state
    if hasattr(dm, 'home_tab_data') and dm.home_tab_data is not None:
        avg_values = dm.home_tab_data.get_average_kpi_values_per_state()

        # Check if avg_values is None and provide default values if it is
        if avg_values is None:
            avg_transaction_count = raw_value
            avg_total_value = raw_value
            avg_transaction_value = raw_value
        else:
            avg_transaction_count, avg_total_value, avg_transaction_value = avg_values

        if card_id == ID.KPI_CARD_AMT_TRANSACTIONS:
            comparison_value = avg_transaction_count
            tooltip_id = ID.KPI_CARD_AMT_TRANSACTIONS_TOOLTIP
        elif card_id == ID.KPI_CARD_SUM_OF_TRANSACTIONS:
            comparison_value = avg_total_value
            tooltip_id = ID.KPI_CARD_SUM_OF_TRANSACTIONS_TOOLTIP
        elif card_id == ID.KPI_CARD_AVG_TRANSACTION_AMOUNT:
            comparison_value = avg_transaction_value
            tooltip_id = ID.KPI_CARD_AVG_TRANSACTION_AMOUNT_TOOLTIP
        else:
            comparison_value = raw_value  # Default to same value (no difference)
            tooltip_id = None
    else:
        comparison_value = raw_value  # Default to same value (no difference)
        tooltip_id = None

    # Create card body with comparison to average per state
    card_body = create_kpi_card_body(raw_value, comparison_value, config["format_fn"], None, tooltip_id)

    return dbc.Card(
        className="kpi-card",
        id=str(card_id.value),
        children=[
            dbc.CardHeader(
                children=[
                    icon,
                    html.P(value_str, className="kpi-card-value kpi-number-value"),
                    html.P(config["title"], className="kpi-card-title"),
                ]
            ),
            card_body
        ]
    )
