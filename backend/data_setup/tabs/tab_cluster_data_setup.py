import json
import pandas as pd
import datetime
import plotly.express as px
from sklearn.cluster import KMeans
from backend.data_setup.tabs.tab_merchant_data_setup import get_my_transactions_mcc_users



# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
my_mcc["mcc"] = my_mcc["mcc"].astype(int)
#-----------------prepare data file-----------------------
my_data_file = get_my_transactions_mcc_users() # imported from tab_merchant_data_setup
# add age_group
bins = [0, 25, 35, 45, 55, 65, 200]
labels = ['<25', '26–35', '36–45', '46–55', '56–65', '65+']
my_data_file['age_group'] = pd.cut(my_data_file['current_age'], bins=bins, labels=labels)

print(my_data_file.head())
print(my_data_file.dtypes)

#---------------------------------------------------------

def get_cluster_merchant_group_dropdown():
    my_df = my_mcc
    my_list = sorted(my_df['merchant_group'].unique().tolist())
    my_list.insert(0, 'All Merchant Groups')
    return my_list

def prepare_cluster_data(df: pd.DataFrame, merchant_group) -> pd.DataFrame:
    # Optional: Merchant Group filter
    if merchant_group != 'All Merchant Groups':
        df = df[df['merchant_group'] == merchant_group].copy()

    df['age_group_plot'] = df['age_group']  # for plotting

    # Aggregation per client_id
    agg = df.groupby('client_id').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum'),
        age_group=('age_group_plot', 'first')  # one age group per client
    ).reset_index()

    agg['average_value'] = agg['total_value'] / agg['transaction_count']

    # Check the number of data points
    n_samples = len(agg)

    # Clustering 1: total_value vs count
    n_clusters_total = min(4, n_samples)
    if n_clusters_total >= 1:
        kmeans_total = KMeans(n_clusters=n_clusters_total, random_state=42, n_init=30)
        agg['cluster_total'] = kmeans_total.fit_predict(agg[['transaction_count', 'total_value']])
    else:
        agg['cluster_total'] = 0  # fallback for 0 rows
    agg['cluster_total_str'] = agg['cluster_total'].astype(str)

    # Clustering 2: average_value vs count
    n_clusters_avg = min(4, n_samples)
    if n_clusters_avg >= 1:
        kmeans_avg = KMeans(n_clusters=n_clusters_avg, random_state=42, n_init=30)
        agg['cluster_avg'] = kmeans_avg.fit_predict(agg[['transaction_count', 'average_value']])
    else:
        agg['cluster_avg'] = 0
    agg['cluster_avg_str'] = agg['cluster_avg'].astype(str)

    return agg

def make_cluster_plot(df_agg: pd.DataFrame, mode='total_value', age_group_mode='all'):
    cluster_column = 'cluster_total_str' if mode == 'total_value' else 'cluster_avg_str'

    fig = px.scatter(
        df_agg,
        x='transaction_count',
        y='total_value' if mode == 'total_value' else 'average_value',
        color=cluster_column,
        hover_data=['client_id', 'transaction_count', 'total_value', 'average_value'],
        title=f'Clustering: {"Total Value" if mode == "total_value" else "Average Value"}',
        facet_col='age_group' if age_group_mode == 'grouped' else None,
        category_orders={"age_group": ['<25', '26–35', '36–45', '46–55', '56–65', '65+']}
    )

    fig.update_layout(showlegend=False)
    return fig