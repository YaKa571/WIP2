import pandas as pd
from dash import Input, Output, callback

import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager
from components.rightcolumn.tabs.tab_user import create_kpi_value_text
from frontend.component_ids import ID

dm = DataManager.get_instance()
COLOR_BLUE_MAIN = "#2563eb"


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
    Updates the four KPI boxes for the selected user or card.
    Priority: Card ID, then User ID.
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
    Shows the credit limit for the selected user (sum of all cards) or card.
    Priority: Card ID.
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
    # Determine dark mode
    dark_mode = bool(n_clicks_dark and n_clicks_dark % 2 == 1)

    # Card ID prioritization
    if card_id and str(card_id).strip():
        try:
            card_row = dm.df_cards[dm.df_cards["id"] == int(card_id)]
            if not card_row.empty:
                user_id = int(card_row.iloc[0]["client_id"])
            else:
                return comp_factory.create_empty_figure()
        except Exception as e:
            return comp_factory.create_empty_figure()

    if not user_id or str(user_id).strip() == "":
        return comp_factory.create_empty_figure()

    try:
        uid = int(user_id)
    except Exception as e:
        return comp_factory.create_empty_figure()

    df_tx = dm.df_transactions[dm.df_transactions["client_id"] == uid]

    if df_tx.empty:
        return comp_factory.create_empty_figure()

    agg = df_tx.groupby(["merchant_id", "mcc"]).agg(
        tx_count=("amount", "size"),
        total_sum=("amount", "sum")
    ).reset_index()

    # MCC Description if available
    y_col = "mcc_desc" if hasattr(dm, "mcc_dict") else "merchant_id"

    if y_col == "mcc_desc":
        def get_mcc_desc(mcc):
            try:
                return dm.mcc_dict.get(str(int(mcc)), "Unknown")
            except Exception:
                return "Unknown"

        agg["mcc_desc"] = agg["mcc"].apply(get_mcc_desc)

    # Sorting
    if sort_by == "count":
        agg = agg.sort_values("tx_count", ascending=False)
        x_col, x_title = "tx_count", "Transaction Count"

    else:
        agg = agg.sort_values("total_sum", ascending=False)
        x_col, x_title = "total_sum", "Total Amount"

    agg = agg.head(10)

    if agg.empty:
        return comp_factory.create_empty_figure()

    hover_template = (
        "🏷️ <b>MCC:</b> %{customdata[0]}<br>"
        "📝 <b>Description:</b> %{x}<br>"
        "🆔 <b>Merchant ID:</b> %{customdata[1]}<br>"
        "💰 <b>Sum:</b> $%{y:,.2f}<br>"
        "<extra></extra>"
    )

    fig = comp_factory.create_bar_chart(
        df=agg,
        x=y_col,
        y=x_col,
        custom_data=["mcc", "merchant_id"],
        hover_template=hover_template,
        labels={x_col: x_title, y_col: "Merchant"},
        bar_color=COLOR_BLUE_MAIN,
        showlegend=False,
        dark_mode=dark_mode
    )

    fig.update_xaxes(showticklabels=False)

    return fig
