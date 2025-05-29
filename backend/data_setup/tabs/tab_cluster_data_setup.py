import json

import pandas as pd
import plotly.express as px
from dash import html
from sklearn.cluster import KMeans

from backend.data_setup.tabs.tab_merchant_data_setup import get_my_transactions_mcc_users

# TODO: Re-organize this file to separate out the data setup for each tab
#  See tab_home_data.py or tab_user_data.py for examples and data_manager.py
#  Data --> Here
#  Tab components --> components/tabs/tab_cluster_components.py

# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
my_mcc["mcc"] = my_mcc["mcc"].astype(int)

# -----------------prepare data file-----------------------
my_data_file = get_my_transactions_mcc_users()  # imported from tab_merchant_data_setup
# add age_group
bins = [0, 25, 35, 45, 55, 65, 200]
labels = ['<25', '26–35', '36–45', '46–55', '56–65', '65+']
my_data_file['age_group'] = pd.cut(my_data_file['current_age'], bins=bins, labels=labels)

# print(my_data_file.head())
# print(my_data_file.dtypes)

# ---------------------------------------------------------
cluster_colors = {
    "0": "#56B4E9",  # light blue
    "1": "#D55E00",  # reddish brown
    "2": "#009E73",  # teal green
    "3": "#E69F00",  # orange
    "4": "#0072B2",  # dark blue
    "5": "#F0E442",  # yellow
    "6": "#CC79A7",  # pink/magenta
    "7": "#999999",  # grey
    "8": "#ADFF2F",  # light green
    "9": "#87CEEB"  # sky blue
}


def get_cluster_merchant_group_dropdown():
    """
    Generate a sorted list of unique merchant groups for a dropdown menu.

    Returns:
    list: Sorted list of merchant groups with 'All Merchant Groups' as the first option.
    """
    my_df = my_mcc
    my_list = sorted(my_df['merchant_group'].unique().tolist())
    my_list.insert(0, 'All Merchant Groups')
    return my_list


def prepare_cluster_data(df: pd.DataFrame, merchant_group) -> pd.DataFrame:
    """
    Prepare and cluster transaction data based on transaction count and value.

    Args:
        df (pd.DataFrame): DataFrame containing transaction data.
        merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

    Returns:
         pd.DataFrame: Aggregated data with cluster labels based on total and average transaction values.
    """
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
    """
    Create a scatter plot showing clusters based on transaction data.

    Args:
        df_agg (pd.DataFrame): Aggregated data with cluster labels.
        mode (str): 'total_value' or 'average_value' to select which clustering to display.
        age_group_mode (str): 'all' for no faceting, 'grouped' to facet by age group.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly scatter plot figure.
    """
    cluster_column = 'cluster_total_str' if mode == 'total_value' else 'cluster_avg_str'
    y_column = 'total_value' if mode == 'total_value' else 'average_value'

    fig = px.scatter(
        df_agg,
        x='transaction_count',
        y=y_column,
        color=cluster_column,
        color_discrete_map=cluster_colors,
        hover_data=['client_id', 'transaction_count', 'total_value', 'average_value'],
        title=f'Cluster per age group {"total value" if mode == "total_value" else "average value"}',
        facet_col='age_group' if age_group_mode == 'grouped' else None,
        facet_col_wrap=3,
        category_orders={"age_group": ['<25', '26–35', '36–45', '46–55', '56–65', '65+']},
        labels={"age_group": " "}
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_layout(showlegend=False)

    return fig


def create_cluster_legend(mode: str, df: pd.DataFrame) -> html.Div:
    """
    Create an HTML legend describing clusters based on transaction or income vs expenses data.

    Args:
        mode (str): Mode of clustering, options include 'total_value', 'average_value', 'inc_vs_exp'.
        df (pd.DataFrame): DataFrame containing clustering data.

    Returns:
        html.Div: Dash HTML Div containing legend items describing each cluster.
    """
    cluster_col = {
        'total_value': 'cluster_total',
        'average_value': 'cluster_avg',
        'inc_vs_exp': 'cluster_inc_vs_exp'
    }[mode]

    items = []

    if mode == 'total_value':
        x_col, y_col = 'transaction_count', 'total_value'
    elif mode == 'average_value':
        x_col, y_col = 'transaction_count', 'average_value'
    elif mode == 'inc_vs_exp':
        x_col, y_col = 'yearly_income', 'total_expenses'
    else:
        x_col, y_col = None, None

    # Quantiles for categorization
    x_quantiles = df[x_col].quantile([0.33, 0.66]) if x_col else None
    y_quantiles = df[y_col].quantile([0.33, 0.66]) if y_col else None

    def categorize(value, quantiles):
        if value <= quantiles.iloc[0]:
            return 'low'
        elif value <= quantiles.iloc[1]:
            return 'medium'
        else:
            return 'high'

    # basic description
    base_desc_map = {
        ('low', 'low'): "Low {} and low {}",
        ('low', 'medium'): "Low {} and moderate {}",
        ('low', 'high'): "Low {} and high {}",
        ('medium', 'low'): "Moderate {} and low {}",
        ('medium', 'medium'): "Moderate {} and moderate {}",
        ('medium', 'high'): "Moderate {} and high {}",
        ('high', 'low'): "High {} and low {}",
        ('high', 'medium'): "High {} and moderate {}",
        ('high', 'high'): "High {} and high {}"
    }

    # support function
    def compare_values(val1, val2, threshold_ratio=0.05):
        """
        Compare two values and return a string indicating relative difference.

        Args:
            val1 (float): First value.
            val2 (float): Second value.
            threshold_ratio (float): Threshold to consider values approximately equal.

        Returns:
            str: Description of relative difference ('approximately equal', 'slightly higher', 'slightly lower').
        """
        diff = val2 - val1
        if abs(diff) / max(abs(val1), 1e-6) < threshold_ratio:
            return "approximately equal"
        elif diff > 0:
            return "slightly higher"
        else:
            return "slightly lower"

    descriptions = {}
    means = {}  # Cluster ID -> (x_mean, y_mean)

    # first round, generate descriptions
    for cl in sorted(df[cluster_col].unique()):
        sub_df = df[df[cluster_col] == cl]

        x_mean = sub_df[x_col].mean()
        y_mean = sub_df[y_col].mean()
        means[cl] = (x_mean, y_mean)

        x_cat = categorize(x_mean, x_quantiles)
        y_cat = categorize(y_mean, y_quantiles)

        base_desc = base_desc_map.get((x_cat, y_cat), "Cluster characteristics unknown")
        base_desc_filled = base_desc.format(x_col.replace('_', ' '), y_col.replace('_', ' '))
        descriptions[cl] = base_desc_filled

    # check if description already exists
    desc_to_clusters = {}
    for cl, desc in descriptions.items():
        desc_to_clusters.setdefault(desc, []).append(cl)

    items = []
    for desc, clusters_with_desc in desc_to_clusters.items():
        if len(clusters_with_desc) == 1:
            # if description does not exist yet
            cl = clusters_with_desc[0]
            color = cluster_colors.get(str(cl), "#000000")
            items.append(
                html.Div(
                    style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
                    children=[
                        html.Div(
                            style={"width": "20px", "height": "20px", "backgroundColor": color, "marginRight": "8px"}),
                        html.Span(f"Cluster {cl}: {desc}")
                    ]
                )
            )
        else:
            # more detailed description, if description already exists
            clusters_sorted = sorted(clusters_with_desc, key=lambda c: means[c][0])
            base_desc = desc
            for i, cl in enumerate(clusters_sorted):
                color = cluster_colors.get(str(cl), "#000000")
                suffix = ""
                if i > 0:

                    prev_cl = clusters_sorted[i - 1]
                    prev_x, prev_y = means[prev_cl]
                    x_mean, y_mean = means[cl]

                    x_comp = compare_values(prev_x, x_mean)
                    y_comp = compare_values(prev_y, y_mean)

                    add_parts = []
                    if x_comp != "approximately equal":
                        add_parts.append(f"{x_comp} {x_col.replace('_', ' ')}")
                    if y_comp != "approximately equal":
                        add_parts.append(f"{y_comp} {y_col.replace('_', ' ')}")

                    if add_parts:
                        suffix = " (" + ", ".join(add_parts) + ")"
                    else:
                        suffix = " (similar characteristics)"

                items.append(
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
                        children=[

                            html.Div(style={"width": "20px", "height": "20px", "backgroundColor": color,
                                            "marginRight": "8px"}),
                            html.Span(f"Cluster {cl}: {base_desc}{suffix}")

                        ]
                    )
                )

    return html.Div(items)


def prepare_inc_vs_exp_cluster_data(df: pd.DataFrame, merchant_group) -> pd.DataFrame:
    """
    Prepare and cluster data based on yearly income versus total expenses.

    Args:
        df (pd.DataFrame): DataFrame containing transaction data.
        merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

    Returns:
        pd.DataFrame: Aggregated data with clusters for income vs expenses.
    """
    # Filtering
    if merchant_group != 'All Merchant Groups':
        df = df[df['merchant_group'] == merchant_group].copy()

    # Aggregation per client_id
    agg = df.groupby('client_id').agg(
        total_expenses=('amount', 'sum'),
        yearly_income=('yearly_income', 'first'),
        age_group=('age_group', 'first')
    ).reset_index()

    # drop NaNs
    agg = agg.dropna(subset=['total_expenses', 'yearly_income'])

    n_samples = len(agg)
    n_clusters = min(4, n_samples)

    if n_clusters >= 1:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=30)
        agg['cluster_inc_vs_exp'] = kmeans.fit_predict(agg[['yearly_income', 'total_expenses']])
    else:
        agg['cluster_inc_vs_exp'] = 0

    agg['cluster_inc_vs_exp_str'] = agg['cluster_inc_vs_exp'].astype(str)
    return agg


def make_inc_vs_exp_plot(df_agg: pd.DataFrame, age_group_mode='all'):
    """
    Create a scatter plot for clusters of income versus expenses data.

    Args:
        df_agg (pd.DataFrame): Aggregated data with income vs expenses clusters.
        age_group_mode (str): 'all' for no faceting, 'grouped' to facet by age group.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly scatter plot figure.
    """
    fig = px.scatter(
        df_agg,
        x='yearly_income',
        y='total_expenses',
        color='cluster_inc_vs_exp_str',
        color_discrete_map=cluster_colors,
        hover_data=['client_id', 'yearly_income', 'total_expenses'],
        title='Cluster per age group Income vs Expenses',
        facet_col='age_group' if age_group_mode == 'grouped' else None,
        facet_col_wrap=3,
        category_orders={"age_group": ['<25', '26–35', '36–45', '46–55', '56–65', '65+']},
        labels={"age_group": " "}
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_layout(showlegend=False)
    return fig
