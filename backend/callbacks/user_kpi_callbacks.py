import pandas as pd
from dash import Input, Output, callback
from backend.data_manager import DataManager

@callback(
    Output("kpi-user-tx-count", "children"),
    Output("kpi-user-tx-sum", "children"),
    Output("kpi-user-tx-avg", "children"),
    Output("kpi-user-card-count", "children"),
    Output("user-credit-limit-box", "children"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
)
def update_user_kpis(user_id, card_id):
    """
    Callback zur Aktualisierung der vier KPIs und des Kreditlimits.
    Berücksichtigt sowohl User ID als auch Card ID (Card hat Priorität).
    """
    dm = DataManager.get_instance()

    # Standardwerte anzeigen, wenn nichts eingegeben
    if (not user_id or user_id.strip() == "") and (not card_id or card_id.strip() == ""):
        return (
            "Amount of Transactions",
            "Total Sum",
            "Average Amount",
            "Amount of Cards",
            "Credit Limit"
        )
    try:
        data = None

        # Card ID hat Priorität
        if card_id and card_id.strip() != "":
            cid = int(card_id)
            data = dm.get_card_kpis(cid)
        elif user_id and user_id.strip() != "":
            uid = int(user_id)
            data = dm.get_user_kpis(uid)
        else:
            return ("Invalid",) * 5

        # Keine Daten gefunden
        if data is None or (data["amount_of_transactions"] == 0 and data["amount_of_cards"] == 0):
            return ("No data", "No data", "No data", "No data", "No data")

        # Kreditlimit
        if data["credit_limit"] is None or pd.isna(data["credit_limit"]):
            credit_limit_str = "Credit Limit: Not found"
        else:
            credit_limit_str = f"Credit Limit: ${data['credit_limit']:,.2f}"

        return (
            f"Transactions: {data['amount_of_transactions']}",
            f"Total Sum: ${data['total_sum']:,.2f}",
            f"Average: ${data['average_amount']:,.2f}",
            f"Cards: {data['amount_of_cards']}",
            credit_limit_str
        )
    except Exception as e:
        print("Error:", str(e))
        return ("Invalid",) * 5
