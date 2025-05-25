from dash import Output, Input, callback, html
import pandas as pd

# Dummy-Daten (gleich wie in Tabelle)
dummy_table_data = [
    {"client_id": 123, "amount": "$999.99", "city": "New York", "method": "Online"},
    {"client_id": 456, "amount": "$720.00", "city": "Los Angeles", "method": "Swipe"},
    {"client_id": 789, "amount": "$310.50", "city": "Chicago", "method": "Online"},
    {"client_id": 321, "amount": "$845.20", "city": "Houston", "method": "Swipe"},
    {"client_id": 654, "amount": "$1120.90", "city": "San Diego", "method": "Online"},
]

df = pd.DataFrame(dummy_table_data)

@callback(
    Output("fraud-detail-panel", "children"),
    Input("fraud-table", "active_cell")
)
def show_fraud_detail(cell):
    if cell is None:
        return "ℹ️ Click on a transaction to see details here."

    row_idx = cell["row"]
    row = df.iloc[row_idx]

    return html.Div([
        html.H5("🔎 Selected Transaction:"),
        html.Ul([
            html.Li(f"Client ID: {row['client_id']}"),
            html.Li(f"Amount: {row['amount']}"),
            html.Li(f"City: {row['city']}"),
            html.Li(f"Method: {row['method']}"),
        ])
    ])
