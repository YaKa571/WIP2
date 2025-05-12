from dash import Input, Output, callback, callback_context, html
from sklearn.cluster import KMeans
from backend.data_manager import DataManager
from frontend.component_ids import ID
import pandas as pd
"""
callbacks and logic of tab cluster
"""

# Data Files
dm=DataManager.get_instance()
my_df_transactions=dm.df_transactions
# Test Data File
my_test_df = pd.DataFrame({'client_id': [1,1,2,2,3,4,4,4,5,1,1,1,6],
                           'amount': [100,150,10,20,500,5,10,15,1000,250,4500,30,450]
                           })

# Aggregation per user
my_test_agg = my_test_df.groupby('client_id').agg(
    transaction_count=('amount', 'count'),
    total_amount=('amount', 'sum')).reset_index()
print(my_test_agg)
# Clustering
kmeans_default = KMeans(n_clusters=4, n_init=20)

# Callback
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