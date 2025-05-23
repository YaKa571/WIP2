import pandas as pd
from dash import Input, Output, callback

import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_user_data_setup import aggregate_transaction_data, get_user_transactions, \
    get_valid_user_id, configure_chart_parameters, create_bar_chart_figure
from components.rightcolumn.tabs.tab_user import create_kpi_value_text
from frontend.component_ids import ID

dm = DataManager.get_instance()


# === Callback: KPI-Boxes (Transactions, Sum, Average, Cards) ===
@callback(
    Output(ID.USER_KPI_TX_COUNT, "children"),
    Output(ID.USER_KPI_TX_SUM, "children"),
    Output(ID.USER_KPI_TX_AVG, "children"),
    Output(ID.USER_KPI_CARD_COUNT, "children"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
)
def update_user_kpis(user_id, card_id):
    """
    Updates and returns user KPI values based on the provided user ID or card ID. The method
    fetches data from the appropriate source depending on the input provided and generates
    KPI texts for display. If no valid data is entered, it provides default or error messages.

    Arguments:
        user_id (str | None): The user ID input value. Expected to be a string or None.
        card_id (str | None): The card ID input value. Expected to be a string or None.

    Returns:
        tuple:
            A tuple containing four strings:
            - The number of transactions.
            - The total sum of transactions formatted as currency.
            - The average transaction amount formatted as currency.
            - The number of cards.
            Each value is returned in a string format. If input is invalid or no data is found,
            default or error texts are returned instead.
    """
    # Show default text if nothing entered
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return ("...",) * 4

    try:
        if card_id and str(card_id).strip():
            data = dm.get_card_kpis(int(card_id))
        elif user_id and str(user_id).strip():
            data = dm.get_user_kpis(int(user_id))
        else:
            return (create_kpi_value_text("INVALID", True),) * 4

        # No data found
        if data is None or (data["amount_of_transactions"] == 0 and data["amount_of_cards"] == 0):
            return (create_kpi_value_text("NO DATA", True),) * 4

        return (
            create_kpi_value_text(f"{data['amount_of_transactions']}"),
            create_kpi_value_text(f"${data['total_sum']:,.2f}"),
            create_kpi_value_text(f"${data['average_amount']:,.2f}"),
            create_kpi_value_text(f"{data['amount_of_cards']}"),
        )

    except Exception as e:
        print("Error (KPI-Boxes):", str(e))
        return (
            create_kpi_value_text("INVALID", True),
        ) * 4


# === Callback: Credit Limit Box ===
@callback(
    Output(ID.USER_CREDIT_LIMIT_BOX, "children"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
)
def update_credit_limit(user_id, card_id):
    """
    This function is a callback designed to update and display the credit limit based on
    the provided user ID or card ID input. The function first determines if a valid user
    ID or card ID is supplied, then attempts to retrieve the associated credit limit from
    a data management utility. It generates formatted text to represent the credit limit
    or an appropriate error message if retrieval fails.

    Parameters:
    user_id: str
        The input value representing the user ID. It is expected to be a string,
        but can be converted to an integer if necessary.
    card_id: str
        The input value representing the card ID. It is expected to be a string,
        but can be converted to an integer if necessary.

    Returns:
    str
        Returns a string containing the formatted credit limit in dollars if available,
        or corresponding error messages such as "NO DATA," "INVALID," or ellipsis ("...")
        when inputs or operations are invalid or data is unavailable.

    Raises:
    Exception
        Any unexpected error that occurs during the retrieval or processing flow will
        be caught, and an "INVALID" message will be returned to the user interface.
    """
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return "..."

    try:
        if card_id and str(card_id).strip():
            limit = dm.get_credit_limit(card_id=int(card_id))
        elif user_id and str(user_id).strip():
            limit = dm.get_credit_limit(user_id=int(user_id))
        else:
            return create_kpi_value_text("INVALID", True)
        if limit is None or pd.isna(limit):
            return create_kpi_value_text("NO DATA", True)
        return create_kpi_value_text(f"${limit:,.2f}")
    except Exception as e:
        print("Error (Credit Limit):", str(e))
        return create_kpi_value_text("INVALID", True)


# === Callback: Merchant Bar Chart (bottom) ===
@callback(
    Output(ID.USER_MERCHANT_BAR_CHART, "figure"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
    Input(ID.USER_MERCHANT_SORT_DROPDOWN, "value"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks"),
)
def update_merchant_bar_chart(user_id, card_id, sort_by, n_clicks_dark):
    """
    Updates the merchant bar chart figure based on user input and selected options. The chart reflects aggregated
    transaction data for a specific user, with sorting and display options, optionally including dark mode.

    Args:
        user_id (str or None): The ID of the user whose transaction data is to be displayed. A `None` value indicates
            no user selection.
        card_id (str or None): The ID of the card associated with the selected user. A `None` value indicates
            no specific card selection.
        sort_by (str or None): The sorting criteria for aggregating transaction data. A `None` value uses the default
            sort order.
        n_clicks_dark (int or None): The number of clicks toggling dark mode. A `None` value or 0 indicates dark
            mode is disabled.

    Returns:
        plotly.graph_objs._figure.Figure: A figure object representing the merchant bar chart. Returns an empty figure
            if the user ID is invalid, no transactions exist for the user, or no aggregation data is available.
    """
    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    # Get valid user ID
    try:
        valid_user_id = get_valid_user_id(user_id, card_id)
        if not valid_user_id:
            return comp_factory.create_empty_figure()
    except ValueError:
        return comp_factory.create_empty_figure()

    # Get transaction data
    df_tx = get_user_transactions(valid_user_id)
    if df_tx.empty:
        return comp_factory.create_empty_figure()

    # Process transaction data
    agg_data = aggregate_transaction_data(df_tx)
    if agg_data.empty:
        return comp_factory.create_empty_figure()

    # Configure chart parameters
    chart_params = configure_chart_parameters(agg_data, sort_by)

    return create_bar_chart_figure(agg_data, chart_params, dark_mode)
