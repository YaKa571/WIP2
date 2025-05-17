import pandas as pd
import plotly.express as px
from dash import Input, Output, callback
from backend.data_manager import DataManager

# ==== Callback 1: User KPIs (Anzahl Transaktionen, Summe, Durchschnitt, Karten) ====
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
    Aktualisiert die vier KPI-Boxen im User-Tab.
    Card ID hat Priorität, sonst User ID.
    """
    dm = DataManager.get_instance()

    # Standardwerte anzeigen, wenn nichts eingegeben wurde
    if (not user_id or str(user_id).strip() == "") and (not card_id or str(card_id).strip() == ""):
        return (
            "Amount of Transactions",
            "Total Sum",
            "Average Amount",
            "Amount of Cards"
        )
    try:
        data = None

        # Card ID hat Priorität
        if card_id and str(card_id).strip() != "":
            cid = int(card_id)
            data = dm.get_card_kpis(cid)
        elif user_id and str(user_id).strip() != "":
            uid = int(user_id)
            data = dm.get_user_kpis(uid)
        else:
            return ("Invalid",) * 4

        # Keine Daten gefunden
        if data is None or (data["amount_of_transactions"] == 0 and data["amount_of_cards"] == 0):
            return ("No data",) * 4

        return (
            f"Transactions: {data['amount_of_transactions']}",
            f"Total Sum: ${data['total_sum']:,.2f}",
            f"Average: ${data['average_amount']:,.2f}",
            f"Cards: {data['amount_of_cards']}"
        )
    except Exception as e:
        print("Error (KPI-Boxen):", str(e))
        return ("Invalid",) * 4

# ==== Callback 2: Kreditlimit-Box ====
@callback(
    Output("user-credit-limit-box", "children"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
)
def update_credit_limit(user_id, card_id):
    """
    Zeigt das Kreditlimit (Summe aller Karten) für User oder Karte.
    Card ID hat Priorität.
    """
    dm = DataManager.get_instance()

    # Standardwert
    if (not user_id or str(user_id).strip() == "") and (not card_id or str(card_id).strip() == ""):
        return "Credit Limit"

    try:
        # Card ID hat Priorität
        if card_id and str(card_id).strip() != "":
            cid = int(card_id)
            limit = dm.get_credit_limit(card_id=cid)
            if limit is None or pd.isna(limit):
                return "Credit Limit: Not found"
            else:
                return f"Credit Limit: ${limit:,.2f}"

        elif user_id and str(user_id).strip() != "":
            uid = int(user_id)
            limit = dm.get_credit_limit(user_id=uid)
            if limit is None or pd.isna(limit):
                return "Credit Limit: Not found"
            else:
                return f"Credit Limit: ${limit:,.2f}"

        else:
            return "Invalid"

    except Exception as e:
        print("Error (Kreditlimit):", str(e))
        return "Invalid"

# ==== Callback 3: Merchant-Bar-Chart unterhalb der KPIs (optional, falls schon drin dann ignorieren) ====
@callback(
    Output("user-bar-chart", "figure"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
    Input("user-bar-chart-sort-dropdown", "value"),
)
def update_merchant_bar_chart(user_id, card_id, sort_by):
    """
    Callback zur Aktualisierung des Händler-Bar-Charts unterhalb der KPIs.
    """
    dm = DataManager.get_instance()

    # Finde relevanten user_id (bei Card ID priorisieren)
    if card_id and str(card_id).strip() != "":
        try:
            cid = int(card_id)
            card_row = dm.df_cards[dm.df_cards["id"] == cid]
            if not card_row.empty:
                user_id = int(card_row.iloc[0]["client_id"])
            else:
                return px.bar(title="No data")
        except Exception:
            return px.bar(title="Invalid Card ID")

    if not user_id or str(user_id).strip() == "":
        return px.bar()

    try:
        uid = int(user_id)
    except Exception:
        return px.bar()

    # Filtere Transaktionen für diesen User
    df_tx = dm.df_transactions[dm.df_transactions["client_id"] == uid]
    if df_tx.empty:
        return px.bar(title="No data found")

    # Gruppiere nach merchant_id und MCC
    agg = df_tx.groupby(["merchant_id", "mcc"]).agg(
        tx_count=("amount", "size"),
        total_sum=("amount", "sum")
    ).reset_index()

    # Optional: MCC Description ergänzen (falls vorhanden)
    if hasattr(dm, "mcc_dict"):
        def get_mcc_desc(mcc):
            try:
                return dm.mcc_dict.get(str(int(mcc)), "Unknown")
            except Exception:
                return "Unknown"
        agg["mcc_desc"] = agg["mcc"].apply(get_mcc_desc)
        y_col = "mcc_desc"
    else:
        y_col = "merchant_id"

    # Sortierung
    if sort_by == "count":
        agg = agg.sort_values("tx_count", ascending=False)
        x_col = "tx_count"
        x_title = "Transaction Count"
    else:
        agg = agg.sort_values("total_sum", ascending=False)
        x_col = "total_sum"
        x_title = "Total Amount"

    # Nur Top 10 Händler
    agg = agg.head(10)

    # Bar Chart
    fig = px.bar(
        agg,
        x=x_col,
        y=y_col,
        orientation="h",
        labels={x_col: x_title, y_col: "Merchant"},
        title="Top Merchants for this User",
        hover_data={"merchant_id": True, "mcc": True}
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=35, b=0),
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig
