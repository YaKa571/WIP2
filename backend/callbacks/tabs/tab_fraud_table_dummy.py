from dash import Output, Input, callback
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

# Dummy-Daten
dummy_table_data = [
    {"Kundennummer": 123, "amount": "$999.99", "city": "New York", "method": "Online"},
    {"Kundennummer": 456, "amount": "$720.00", "city": "Los Angeles", "method": "Swipe"},
    {"Kundennummer": 789, "amount": "$310.50", "city": "Chicago", "method": "Online"},
    {"Kundennummer": 321, "amount": "$845.20", "city": "Houston", "method": "Swipe"},
    {"Kundennummer": 654, "amount": "$1120.90", "city": "San Diego", "method": "Online"},
]

@callback(
    Output("fraud-table", "children"),
    Input("app-init-trigger", "children")  # trigger bei App-Start
)
def update_dummy_fraud_table(_):
    df = pd.DataFrame(dummy_table_data)

    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
    rows = [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))]
    body = html.Tbody(rows)

    return [header, body]
