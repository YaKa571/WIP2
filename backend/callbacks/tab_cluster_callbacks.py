from dash import Input, Output, callback, callback_context, html
from frontend.component_ids import ID
"""
callbacks and logic of tab cluster
"""

@callback(
    Output(ID.CLUSTER_DROPDOWN_OUTPUT, 'children'),
    Output(ID.CLUSTER_KEY, 'children'),
    Input(ID.CLUSTER_DROPDOWN, 'value')
)
def update_cluster(value):
    if value == "Default":
        key = html.Ul([
            html.Li("Cluster 1", style={"color": "red"}),
            html.Li("Cluster 2", style={"color": "blue"}),
            html.Li("Cluster 3", style={"color": "green"}),
            html.Li("Cluster 4", style={"color": "yellow"}),
        ])
        text = 'Cluster: "Default"'
    elif value == "Age Group":
        key = html.Ul([
            html.Li("Young", style={"color": "red"}),
            html.Li("Middle-aged", style={"color": "blue"}),
            html.Li("Senior", style={"color": "green"}),
        ])
        text = 'Cluster: "Age Group"'
    elif value == "Income vs Expenditures":
        key = html.Ul([
            html.Li("Low Income / High Spending", style={"color": "red"}),
            html.Li("Low Income / Low Spending", style={"color": "blue"}),
            html.Li("High Income / High Spending", style={"color": "green"}),
            html.Li("High Income / Low Spending", style={"color": "yellow"}),
        ])
        text = 'Cluster: "Income vs Expenditures"'
    else:
        key = html.Div("no key available")
        text = "Cluster: Unknown"
    text = text + " TODO: Colortheme"
    return text, html.Div([html.H5("Key:"), key])