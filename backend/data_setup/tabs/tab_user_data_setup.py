import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from components.constants import COLOR_BLUE_MAIN

dm: DataManager = DataManager.get_instance()

# === Constants ===
UNKNOWN_VALUE = "Unknown"
SORT_BY_COUNT = "count"
TRANSACTION_COUNT_TITLE = "USER'S TOP MERCHANTS BY TRANSACTION COUNT"
TOTAL_SPENDING_TITLE = "USER'S TOP MERCHANTS BY TOTAL SPENDING"
HOVER_TEMPLATE_BASE = (
    "🏷️ <b>MCC:</b> %{customdata[0]}<br>"
    "📝 <b>Description:</b> %{customdata[2]}<br>"
    "🆔 <b>Merchant ID:</b> %{customdata[1]}<br>"
)


def get_valid_user_id(user_id, card_id):
    """
    Retrieve a valid user ID based on provided user ID and card ID.

    This function validates and prioritizes the card ID over the user ID to fetch the corresponding
    user's ID. If a valid card ID is provided, it returns the associated client ID. If the card
    ID is invalid or not present but a user ID is provided, it attempts to validate the user ID.
    In case both are invalid or not provided, the function returns None.

    Args:
        user_id (str or int): The user ID to be validated. Can be a string or an integer.
        card_id (str or int): The card ID used to fetch the corresponding user's ID. Can be a
        string or an integer.

    Returns:
        int or None: The validated user ID as an integer, or None if both inputs are invalid
        or empty.
    """
    if card_id and str(card_id).strip():
        try:
            card_row = dm.df_cards[dm.df_cards["id"] == int(card_id)]
            return int(card_row.iloc[0]["client_id"]) if not card_row.empty else None
        except Exception:
            return None

    if not user_id or str(user_id).strip() == "":
        return None

    try:
        return int(user_id)
    except Exception:
        return None


def get_user_transactions(user_id):
    """
    Fetches transactions associated with a specific user from the transactions dataset.

    Parameters:
    user_id: int
        The identifier of the user whose transactions are to be retrieved.

    Returns:
    pandas.DataFrame
        A DataFrame containing all transactions linked to the specified user.
    """
    return dm.df_transactions[dm.df_transactions["client_id"] == user_id]


def aggregate_transaction_data(df_tx):
    """
    Aggregates transaction data by grouping based on merchant ID and MCC, and computes
    the transaction count and total amount sum. Adds an MCC description for each group.

    Parameters:
    df_tx : pandas.DataFrame
        A DataFrame containing transaction data with at least the following columns:
        'merchant_id', 'mcc', and 'amount'.

    Returns:
    pandas.DataFrame
        A new DataFrame containing aggregated transaction data with the following columns:
        'merchant_id', 'mcc', 'tx_count', 'total_sum', and 'mcc_desc'.

    """
    agg = df_tx.groupby(["merchant_id", "mcc"]).agg(
        tx_count=("amount", "size"),
        total_sum=("amount", "sum")
    ).reset_index()

    agg["mcc_desc"] = agg["mcc"].apply(get_mcc_description)
    return agg


def get_mcc_description(mcc):
    """
    Fetches the description for a given MCC (Merchant Category Code).

    This function takes an MCC as input, converts it to an integer, and retrieves
    its description from a predefined dictionary of MCC codes. If the MCC is
    not found or if any error occurs during processing, a default unknown value
    is returned.

    Args:
        mcc: The Merchant Category Code to look up. Can be in any format that
            can be safely converted to an integer.

    Returns:
        str: The description associated with the provided MCC. If the MCC is
        not in the dictionary or an exception occurs, returns a default
        unknown value.
    """
    try:
        return dm.mcc_dict.get(str(int(mcc)), UNKNOWN_VALUE)
    except Exception:
        return UNKNOWN_VALUE


def configure_chart_parameters(agg, sort_by):
    """
    Configures chart parameters based on sorting criteria.

    This function adjusts aggregate data and defines configuration
    parameters for generating a chart. The configuration depends on
    whether the data should be sorted by transaction count or total
    sum. The returned configuration includes columns, titles, and
    hover information.

    Args:
        agg: A DataFrame representing the aggregated data to be used
             for chart creation.
        sort_by: A string indicating the sorting criterion. It can be
                 either a predefined constant for "count" or "sum".

    Returns:
        A dictionary containing the configuration parameters such as
        column names, chart titles, and hover template formats.
    """
    if sort_by == SORT_BY_COUNT:
        agg = agg.sort_values("tx_count", ascending=False)
        return {
            "x_col": "tx_count",
            "x_title": "Transaction Count",
            "hover_last_row": "💳 <b>Transactions:</b> %{y:,}<br>",
            "bar_title": TRANSACTION_COUNT_TITLE
        }
    else:
        agg = agg.sort_values("total_sum", ascending=False)
        return {
            "x_col": "total_sum",
            "x_title": "Total Amount",
            "hover_last_row": "💰 <b>Sum:</b> $%{y:,.2f}<br>",
            "bar_title": TOTAL_SPENDING_TITLE
        }


def create_bar_chart_figure(agg, params, dark_mode):
    """
    Creates a bar chart figure using aggregated data and specific parameters.

    This function generates a bar chart based on the input aggregated data and a set of
    dynamic parameters. It uses a customizable hover template and applies styling for
    dark or light mode. It leverages a component factory to handle chart creation and
    ensures the resulting chart has a consistent appearance with provided labels, colors,
    and settings.

    Args:
        agg (DataFrame): The aggregated data used for plotting the bar chart.
                         Must contain relevant columns required for the chart.
        params (dict): A dictionary of parameters defining the chart configuration.
                       - "x_col" (str): Column name to use for the y-axis values.
                       - "hover_last_row" (str): Additional information to include
                         in hover templates.
                       - "bar_title" (str): The title to display on the chart.
                       - "x_title" (str): The label for the chart's x-axis.
        dark_mode (bool): Determines whether the chart should be styled for dark mode.

    Returns:
        Figure: A Plotly figure object representing the bar chart.
    """
    hover_template = HOVER_TEMPLATE_BASE + params["hover_last_row"] + "<extra></extra>"

    return comp_factory.create_bar_chart(
        df=agg,
        x="merchant_id",
        y=params["x_col"],
        title=params["bar_title"],
        custom_data=["mcc", "merchant_id", "mcc_desc"],
        hover_template=hover_template,
        labels={params["x_col"]: params["x_title"], "merchant_id": "Merchant ID"},
        bar_color=COLOR_BLUE_MAIN,
        showlegend=False,
        dark_mode=dark_mode
    )
