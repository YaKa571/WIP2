from dash import Input, Output, callback
from backend.data_manager import DataManager


@callback(
    Output("kpi-user-tx-count", "children"),
    Output("kpi-user-tx-sum", "children"),
    Output("kpi-user-tx-avg", "children"),
    Output("kpi-user-card-count", "children"),
    Input("user-id-search-input", "value")
)
def update_user_kpis(user_id):
    if not user_id:
        return [
            "Amount of Transactions",
            "Total Sum",
            "Average Amount",
            "Amount of Cards"
        ]

    try:
        uid = int(user_id)
    except ValueError:
        return ["Invalid ID"] * 4

    dm: DataManager = DataManager.get_instance()

    # Filtere Transaktionen anhand ID
    tx = dm.df_transactions[dm.df_transactions["id"] == uid]

    # Karten brauchst du NICHT für die Anzahl – sondern die Info kommt aus df_users!
    user_row = dm.df_users[dm.df_users["id"] == uid]

    if tx.empty and user_row.empty:
        return ["No data"] * 4

    # Berechnungen
    tx_count = len(tx)
    tx_sum = tx["amount"].sum()
    tx_avg = tx["amount"].mean() if tx_count > 0 else 0

    # Kartenanzahl aus users_data.csv
    card_count = int(user_row.iloc[0]["num_credit_cards"]) if not user_row.empty else 0

    return (
        f"Transactions: {tx_count}",
        f"Total Sum: ${tx_sum:,.2f}",
        f"Average: ${tx_avg:,.2f}",
        f"Cards: {card_count}"
    )
