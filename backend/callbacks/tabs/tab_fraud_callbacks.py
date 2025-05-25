from dash import Output, Input, callback
from backend.data_manager import DataManager

dm = DataManager.get_instance()

@callback(
    Output("fraud-trans-count", "children"),
    Output("fraud-sum-value", "children"),
    Output("fraud-avg-value", "children"),
    Input("app-init-trigger", "children")  # Dummy trigger bei Start
)
def update_fraud_kpis(_):
    df = dm.df_transactions
    df_fraud = df[df["is_fraud"] == 1]

    amount = len(df_fraud)
    total = df_fraud["amount"].sum()
    avg = df_fraud["amount"].mean()

    return (
        f"{amount:,}",                        # z. B. 50,000
        f"${total:,.2f}",                    # z. B. $2,123,456.78
        f"${avg:,.2f}" if amount else "$0"   # Durchschnitt
    )
