import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

import components.factories.component_factory as comp_factory
from backend.callbacks.tabs.tab_merchant_callbacks import ID_TO_MERCHANT_TAB
from backend.data_manager import DataManager
from components.tabs.tab_user_components import get_valid_user_id, configure_chart_parameters, \
    create_bar_chart_figure
from frontend.layout.right.tabs.tab_user import create_kpi_value_text
from frontend.component_ids import ID
import components.constants as const

dm: DataManager = DataManager.get_instance()
TEXT_EMPTY_KPI: str = "Waiting for input..."


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
    Updates user KPI metrics based on a given user ID or card ID. The KPIs updated include
    the transaction count, total transaction sum, average transaction amount, and
    card count associated with either the specified user or card. If no valid
    user ID or card ID is provided, default values indicating no data or invalid input
    are returned. In case of an error during the process, invalid KPI values are returned.

    Args:
        user_id: The ID of the user used to fetch KPI data.
        card_id: The ID of the card used to fetch KPI data.

    Returns:
        A tuple containing updated KPI values for:
            - Transaction count.
            - Total transaction sum formatted as currency.
            - Average transaction amount formatted as currency.
            - Card count.
    """
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return (create_kpi_value_text(TEXT_EMPTY_KPI, True),) * 4

    try:
        if card_id and str(card_id).strip():
            data = dm.user_tab_data.get_card_kpis(int(card_id))
        elif user_id and str(user_id).strip():
            data = dm.user_tab_data.get_user_kpis(int(user_id))
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
    Updates the credit limit information in the user interface based on the provided 
    user ID or card ID. The function determines the credit limit by querying the 
    data manager, formats the limit as a text representation, and returns it to the 
    callback output. If the input values are invalid, missing, or lead to data 
    retrieval issues, user feedback messages are provided accordingly.

    Args:
        user_id (str): The value entered in the user ID search input field. This is 
            used to fetch the credit limit associated with the specific user.
        card_id (str): The value entered in the card ID search input field. This is 
            used to fetch the credit limit associated with the specific card.

    Returns:
        str: A formatted representation of the credit limit, an error message if the 
            inputs are invalid or missing, or a message indicating that no data is 
            available for the specified inputs.
    """
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return create_kpi_value_text(TEXT_EMPTY_KPI, True)

    try:
        if card_id and str(card_id).strip():
            limit = dm.user_tab_data.get_credit_limit(card_id=int(card_id))
        elif user_id and str(user_id).strip():
            limit = dm.user_tab_data.get_credit_limit(user_id=int(user_id))
        else:
            return create_kpi_value_text("INVALID", True)
        if limit is None or pd.isna(limit):
            return create_kpi_value_text("NO DATA", True)
        return create_kpi_value_text(f"${limit:,.2f}")
    except Exception as e:
        print("Error (Credit Limit):", str(e))
        return create_kpi_value_text("INVALID", True)


@callback(
    Output(ID.USER_CREDIT_LIMIT_BAR, "figure"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
)
def update_credit_limit_bar(user_id, card_id):
    """
    Updates the credit limit bar chart visualization for a user based on the provided
    user ID or card ID. The function dynamically creates a horizontal stacked bar chart,
    where each segment represents the credit limit associated with a specific credit card.
    If no valid inputs are provided, or if the inputs do not correspond to any records,
    an empty figure is generated and returned.

    :param user_id: A string or integer representing the user identifier. If provided,
        the function will use the user ID to fetch and process all cards belonging
        to the given user.
    :type user_id: str | int
    :param card_id: A string or integer representing the card identifier. If provided,
        the function will look up the corresponding user ID and fetch relevant
        card details for that user.
    :type card_id: str | int
    :return: A Plotly figure object representing the credit limit bar chart for the user's
        cards. If no data is found, an empty figure is returned.
    :rtype: plotly.graph_objs._figure.Figure
    """
    if card_id and str(card_id).strip():
        card_df = dm.df_cards[dm.df_cards["id"] == int(card_id)]
        if card_df.empty:
            return comp_factory.create_empty_figure()
        user_id = int(card_df.iloc[0]["client_id"])
    elif user_id and str(user_id).strip():
        user_id = int(user_id)
    else:
        return comp_factory.create_empty_figure()

    user_cards = dm.df_cards[dm.df_cards["client_id"] == user_id]
    if user_cards.empty:
        return comp_factory.create_empty_figure()

    # Nach Kreditlimit sortieren (größte zuerst)
    user_cards = user_cards.sort_values("credit_limit", ascending=False).reset_index(drop=True)
    credit_limits = user_cards["credit_limit"].tolist()
    card_ids = user_cards["id"].tolist()

    # 9 Colors as max num of credit cards is 9
    colors = [
        "#36c36a",  # grün
        "#5d9cf8",  # blau
        "#f1b44c",  # gelb-orange
        "#e74c3c",  # rot
        "#8e44ad",  # lila
        "#16a085",  # türkis
        "#f06292",  # pink
        "#f39c12",  # orange
        "#7f8c8d",  # grau
    ]

    fig = go.Figure()
    for i, (limit, card_id) in enumerate(zip(credit_limits, card_ids)):
        fig.add_trace(go.Bar(
            x=[limit],
            y=["Credit Limit"],
            name=f"Card {i + 1}",
            orientation="h",
            marker_color=colors[i % len(colors)],
            marker_line_width=0,
            hovertemplate=(
                "💳 <b>Card:</b> %{customdata[0]}<br>"
                "🆔 <b>ID:</b> %{customdata[1]}<br>"
                "💰 <b>Limit:</b> $%{x:,.2f}<extra></extra>"
            ),
            text=f"${limit:,.2f}",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=14, color="white"),
            offsetgroup=0,
            customdata=[[i + 1, card_id]],
        ))

    fig.update_layout(
        barmode="stack",
        showlegend=False,
        bargap=0,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        xaxis=dict(
            showticklabels=False,
            visible=False,
            range=[0, sum(credit_limits)]
        ),
        yaxis=dict(showticklabels=False, visible=False),
    )

    return fig


# === Callback: Merchant Bar Chart (bottom) ===
@callback(
    Output(ID.USER_MERCHANT_BAR_CHART, "figure"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
    Input(ID.USER_MERCHANT_SORT_DROPDOWN, "value"),
    Input(ID.BUTTON_DARK_MODE_TOGGLE, "n_clicks")
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
    df_tx = dm.user_tab_data.get_user_transactions(valid_user_id)
    if df_tx.empty:
        return comp_factory.create_empty_figure()

    # Process transaction data
    agg_data = dm.user_tab_data.get_user_merchant_agg(valid_user_id)
    if agg_data.empty:
        return comp_factory.create_empty_figure()

    # Configure chart parameters
    chart_params = configure_chart_parameters(agg_data, sort_by)

    return create_bar_chart_figure(agg_data, chart_params, dark_mode)


@callback(
    Output(ID.MERCHANT_INPUT_MERCHANT_ID, "value", allow_duplicate=True),
    # Merchant Tab -> Input -> Search by Merchant ID
    Output(ID.ACTIVE_TAB_STORE, "data", allow_duplicate=True),  # Active Tab Store
    Output(ID.USER_MERCHANT_BAR_CHART, "clickData"),  # User Graph Bar Chart
    Output(ID.MERCHANT_SELECTED_BUTTON_STORE, "data", allow_duplicate=True),  # Merchant Button Store
    Input(ID.USER_MERCHANT_BAR_CHART, "clickData"),
    prevent_initial_call=True
)
def bridge_user_to_merchant_tab(click_data):
    """
    This callback function bridges interactions from the user bar chart to the merchant tab. It updates the merchant input
    field, activates the merchant tab, and resets or sets related data stores. When a user clicks on a bar in the
    user-merchant bar chart, this function extracts the relevant data from the click event and updates the specified
    components accordingly.

    Args:
        click_data: The information about the user's interaction with the
            user-merchant bar chart. Contains details about the specific bar
            that was clicked.

    Returns:
        tuple: A tuple with four elements. The first element is the selected
            Merchant ID to populate the Merchant Input field. The second
            element is the active tab identifier for navigating to the
            Merchant tab. The third element resets the clickData for the bar
            chart. The fourth element updates the merchant selection button
            store data.

    Raises:
        PreventUpdate: This will be raised if the `click_data` is `None`,
            meaning no click event occurred.
    """
    if click_data is None:
        return PreventUpdate

    return click_data["points"][0]["x"], ID.TAB_MERCHANT, None, ID_TO_MERCHANT_TAB.get(
        ID.MERCHANT_BTN_INDIVIDUAL_MERCHANT).value


@callback(
    Output(ID.CARD_ID_SEARCH_INPUT, "disabled"),
    Output(ID.CARD_ID_SEARCH_INPUT, "className"),
    Output(ID.USER_ID_SEARCH_INPUT, "disabled"),
    Output(ID.USER_ID_SEARCH_INPUT, "className"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
)
def toggle_inputs(user_value, card_value):
    """
    Toggles the disabled state and CSS class of search input fields based on the input values.

    This function determines whether the "disabled" attribute and CSS class of the input
    fields for user ID and card ID should be updated based on whether values have been
    input into the respective fields. When one field is filled, the other becomes disabled
    and gets an updated CSS class, indicating its disabled state.

    Parameters:
        user_value (str | None): The current value of the user ID search input.
        card_value (str | None): The current value of the card ID search input.

    Returns:
        tuple[bool, str, bool, str]: A tuple containing four values:
            1. Boolean indicating whether the card ID search input should be disabled.
            2. String representing the updated CSS class for the card ID search input.
            3. Boolean indicating whether the user ID search input should be disabled.
            4. String representing the updated CSS class for the user ID search input.
    """
    base_class = "search-bar-input no-spinner"

    user_filled = bool(user_value and str(user_value).strip())
    card_filled = bool(card_value and str(card_value).strip())

    card_disabled = user_filled
    user_disabled = card_filled

    card_class = f"{base_class} is-disabled" if card_disabled else base_class
    user_class = f"{base_class} is-disabled" if user_disabled else base_class
    return card_disabled, card_class, user_disabled, user_class


@callback(
    Output(ID.USER_TAB_HEADING, "children"),
    Input(ID.USER_ID_SEARCH_INPUT, "value"),
    Input(ID.CARD_ID_SEARCH_INPUT, "value"),
)
def update_tab_heading(user_id, card_id):
    """
    Updates the tab heading dynamically based on user or card IDs.

    This callback function modifies the content of a user tab heading
    based on the provided `user_id` or `card_id` values. It determines
    which identifier is present and returns a corresponding label.
    If both identifiers are empty or invalid, it defaults to a generic
    "User" label.

    Args:
        user_id: The ID of the user to be displayed in the tab heading.
        card_id: The ID of the card to be displayed in the tab heading.

    Returns:
        str: A formatted string representing the tab heading that uses
        the provided user or card ID. Defaults to "User" if neither
        identifier is valid.
    """
    if card_id and str(card_id).strip():
        return f" From Card-ID: {card_id}"
    elif user_id and str(user_id).strip():
        return f"From User-ID: {user_id}"
    else:
        return "User"
