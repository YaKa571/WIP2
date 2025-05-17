import pandas as pd
import plotly.express as px
from dash import Input, Output, callback
from backend.data_manager import DataManager

# === Callback: KPI-Boxes (Transaktionen, Summe, Durchschnitt, Karten) ===
@callback(
    Output("kpi-user-tx-count", "children"),
    Output("kpi-user-tx-sum", "children"),
    Output("kpi-user-tx-avg", "children"),
    Output("kpi-user-card-count", "children"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
)
def update_user_kpis(user_id, card_id):
    """
    Updates the four KPI boxes for the selected user or card.
    Priority: Card ID, then User ID.
    """
    dm = DataManager.get_instance()
    # Show default text if nothing entered
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return (
            "Amount of Transactions",
            "Total Sum",
            "Average Amount",
            "Amount of Cards"
        )
    try:
        if card_id and str(card_id).strip():
            data = dm.get_card_kpis(int(card_id))
        elif user_id and str(user_id).strip():
            data = dm.get_user_kpis(int(user_id))
        else:
            return ("Invalid",) * 4

        # No data found
        if data is None or (data["amount_of_transactions"] == 0 and data["amount_of_cards"] == 0):
            return ("No data",) * 4

        return (
            f"Transactions: {data['amount_of_transactions']}",
            f"Total Sum: ${data['total_sum']:,.2f}",
            f"Average: ${data['average_amount']:,.2f}",
            f"Cards: {data['amount_of_cards']}"
        )
    except Exception as e:
        print("Error (KPI-Boxes):", str(e))
        return ("Invalid",) * 4

# === Callback: Credit Limit Box ===
@callback(
    Output("user-credit-limit-box", "children"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
)
def update_credit_limit(user_id, card_id):
    """
    Shows the credit limit for the selected user (sum of all cards) or card.
    Priority: Card ID.
    """
    dm = DataManager.get_instance()
    if not (user_id and str(user_id).strip()) and not (card_id and str(card_id).strip()):
        return "Credit Limit"
    try:
        if card_id and str(card_id).strip():
            limit = dm.get_credit_limit(card_id=int(card_id))
        elif user_id and str(user_id).strip():
            limit = dm.get_credit_limit(user_id=int(user_id))
        else:
            return "Invalid"
        if limit is None or pd.isna(limit):
            return "Credit Limit: Not found"
        return f"Credit Limit: ${limit:,.2f}"
    except Exception as e:
        print("Error (Credit Limit):", str(e))
        return "Invalid"

# === Callback: Merchant Bar Chart (bottom) ===
@callback(
    Output("user-merchant-bar-chart", "figure"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
    Input("merchant-sort-dropdown", "value"),
)
def update_merchant_bar_chart(user_id, card_id, sort_by):
    """
    Updates the horizontal bar chart with the top merchants for the selected user or card.
    Sorting by total amount (default) or transaction count.
    """
    dm = DataManager.get_instance()
    # Card ID prioritization
    if card_id and str(card_id).strip():
        try:
            card_row = dm.df_cards[dm.df_cards["id"] == int(card_id)]
            if not card_row.empty:
                user_id = int(card_row.iloc[0]["client_id"])
            else:
                return px.bar()
        except Exception:
            return px.bar()
    if not user_id or str(user_id).strip() == "":
        return px.bar()
    try:
        uid = int(user_id)
    except Exception:
        return px.bar()
    df_tx = dm.df_transactions[dm.df_transactions["client_id"] == uid]
    if df_tx.empty:
        return px.bar()
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
        return px.bar()
    fig = px.bar(
        agg,
        x=x_col,
        y=y_col,
        orientation="h",
        labels={x_col: x_title, y_col: "Merchant"},
        hover_data={"merchant_id": True, "mcc": True}
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=35, b=0),
        height=340,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig
