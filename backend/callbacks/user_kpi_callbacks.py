from dash import Input, Output, callback
from backend.data_manager import DataManager

@callback(
    Output("kpi-user-tx-count", "children"),
    Output("kpi-user-tx-sum", "children"),
    Output("kpi-user-tx-avg", "children"),
    Output("kpi-user-card-count", "children"),
    Input("user-id-search-input", "value"),
    Input("card-id-search-input", "value"),
)
def update_user_kpis(user_id, card_id):
    dm: DataManager = DataManager.get_instance()

    # Default-Anzeige
    if (not user_id or user_id == "") and (not card_id or card_id == ""):
        return [
            "Amount of Transactions",
            "Total Sum",
            "Average Amount",
            "Amount of Cards"
        ]

    try:
        if user_id and user_id.strip() != "":
            uid = int(user_id)
            data = dm.get_user_kpis(uid)
        elif card_id and card_id.strip() != "":
            cid = int(card_id)
            data = dm.get_card_kpis(cid)
        else:
            return ["Invalid ID"] * 4
    except Exception:
        return ["Invalid ID"] * 4

    return (
        f"Transactions: {data['amount_of_transactions']}",
        f"Total Sum: ${data['total_sum']:,.2f}",
        f"Average: ${data['average_amount']:,.2f}",
        f"Cards: {data['amount_of_cards']}"
    )
