import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, html
from sklearn.cluster import KMeans

from backend.data_manager import DataManager
from frontend.component_ids import ID

"""
callbacks and logic of tab cluster
"""

# Data Files
dm: DataManager = DataManager.get_instance()
my_df_transactions = dm.df_transactions
# Test Data File
my_test_df = pd.DataFrame({'client_id': [1, 1, 2, 2, 3, 4, 4, 4, 5, 1, 1, 1, 6],
                           'amount': [100, 150, 10, 20, 500, 5, 10, 15, 1000, 250, 4500, 30, 450]
                           })
"""
Data Set Up Test
"""
# Aggregation per user
my_test_agg = my_test_df.groupby('client_id').agg(
    transaction_count=('amount', 'count'),
    total_value=('amount', 'sum')).reset_index()

# Clustering
kmeans_default = KMeans(n_clusters=4, n_init=20)
my_test_agg['cluster'] = kmeans_default.fit_predict(my_test_agg[['transaction_count', 'total_value']])
my_test_agg['cluster_str'] = my_test_agg['cluster'].astype(str)
# print(my_test_agg)
"""
Data Set Up Default
"""
# Aggregation per user
my_transactions_agg = my_df_transactions.groupby('client_id').agg(
    transaction_count=('amount', 'count'),
    total_value=('amount', 'sum')).reset_index()

# Clustering
kmeans_default = KMeans(n_clusters=4, n_init=20)
my_transactions_agg['cluster'] = kmeans_default.fit_predict(my_transactions_agg[['transaction_count', 'total_value']])
my_transactions_agg['cluster_str'] = my_transactions_agg['cluster'].astype(str)

# Callback
@callback(
    Output(ID.CLUSTER_DROPDOWN_OUTPUT, 'children'),
    Output(ID.CLUSTER_GRAPH, 'figure'),
    Output(ID.CLUSTER_KEY, 'children'),
    Input(ID.CLUSTER_DROPDOWN, 'value')
)
def update_cluster(value):
    if value == "Default":
        cluster_colors = {
            "0": "red",
            "1": "blue",
            "2": "green",
            "3": "orange"
        }
        fig = px.scatter(my_transactions_agg, x="transaction_count", y="total_value",
                         color="cluster_str",
                         color_discrete_map=cluster_colors,
                         hover_data=['client_id', 'transaction_count', 'total_value'],
                         title='Cluster: transaction amount/total value')
        key = html.Ul([
            html.Li(f"Cluster {i}", style={"color": cluster_colors[str(i)]})
            for i in range(4)
        ])
        text = 'Cluster: "Default"'
    elif value == "Test":
        cluster_colors = {
            "0": "red",
            "1": "blue",
            "2": "green",
            "3": "orange"
        }
        fig = px.scatter(my_test_agg, x="transaction_count", y="total_value",
                         color="cluster_str",
                         color_discrete_map=cluster_colors,
                         hover_data=['client_id', 'transaction_count', 'total_value'],
                         title='Cluster: transaction amount/total value')
        key = html.Ul([
            html.Li(f"Cluster {i}", style={"color": cluster_colors[str(i)]})
            for i in range(4)
        ])
        text = 'Cluster: "Test"'
    elif value == "Age Group":
        fig = px.scatter()
        key = html.Ul([
            html.Li("Young", style={"color": "red"}),
            html.Li("Middle-aged", style={"color": "blue"}),
            html.Li("Senior", style={"color": "green"}),
        ])
        text = 'Cluster: "Age Group"'
    elif value == "Income vs Expenditures":
        fig = px.scatter()
        key = html.Ul([
            html.Li("Low Income / High Spending", style={"color": "red"}),
            html.Li("Low Income / Low Spending", style={"color": "blue"}),
            html.Li("High Income / High Spending", style={"color": "green"}),
            html.Li("High Income / Low Spending", style={"color": "yellow"}),
        ])
        text = 'Cluster: "Income vs Expenditures"'
    else:
        fig = px.scatter()
        key = html.Div("no key available")
        text = "Cluster: Unknown"
    return text, fig, html.Div([html.H5("Key:"), key])
