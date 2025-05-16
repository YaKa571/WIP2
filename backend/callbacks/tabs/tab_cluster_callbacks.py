import pandas as pd
import plotly.express as px
import datetime
from dash import Input, Output, callback, html
from sklearn.cluster import KMeans

from backend.data_manager import DataManager
from frontend.component_ids import ID

"""
callbacks and logic of tab cluster
"""

# Data Files
dm: DataManager = DataManager.get_instance()
my_transactions = dm.df_transactions
my_users = dm.df_users
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
my_test_agg['cluster_str'] = my_test_agg['cluster'].astype(str) #needed for color scheme allocation
# print(my_test_agg)
"""
Data Set Up Default
"""
# Aggregation per user
my_transactions_agg = my_transactions.groupby('client_id').agg(
    transaction_count=('amount', 'count'),
    total_value=('amount', 'sum')).reset_index()
my_transactions_agg['average_value'] = my_transactions_agg['total_value'] / my_transactions_agg['transaction_count']
# Clustering
kmeans_default_total = KMeans(n_clusters=4, random_state=42, n_init=30)
my_transactions_agg['cluster'] = kmeans_default_total.fit_predict(my_transactions_agg[['transaction_count', 'total_value']])
my_transactions_agg['cluster_str'] = my_transactions_agg['cluster'].astype(str) # needed for color scheme allocation

kmeans_default_avg = KMeans(n_clusters=4, random_state=42, n_init=30)
my_transactions_agg['cluster_average'] = kmeans_default_avg.fit_predict(my_transactions_agg[['transaction_count', 'average_value']])
my_transactions_agg['cluster_average_str'] = my_transactions_agg['cluster_average'].astype(str)
"""
Data Set Up Age Group
"""
my_transactions_users_joined = my_transactions.merge(
    my_users,
    left_on='client_id',
    right_on='id',
    how='left'
)
# compute age group
current_year = datetime.datetime.now().year
my_transactions_users_joined['current_age'] = current_year - my_transactions_users_joined['birth_year']
# TODO set appropriate age groups
def get_age_group(age):
    if age < 25:
        return '0'
    elif age < 35:
        return '1'
    elif age < 45:
        return '2'
    elif age < 55:
        return '3'
    elif age < 65:
        return '4'
    else:
        return '5'

my_transactions_users_joined['age_group'] = my_transactions_users_joined['current_age'].apply(get_age_group)
my_age_group = my_transactions_users_joined.groupby('client_id').agg(
    transaction_count=('amount', 'count'),
    total_value=('amount', 'sum'),
    average_value=('amount', 'mean'),
    age_group=('age_group','first') # first age group of user (data 2010 - 2019)
).reset_index()

my_age_group_clustered = []
for group in my_age_group['age_group'].unique():
    subset = my_age_group[my_age_group['age_group'] == group].copy()

    if len(subset) >= 4:  # KMeans needs a minimum of k points
        kmeans_age_group = KMeans(n_clusters=4, random_state=42, n_init=30)
        subset['cluster'] = kmeans_age_group.fit_predict(subset[['transaction_count', 'total_value']])
        subset['cluster_str'] = subset['cluster'].astype(str)
    else:
        subset['cluster'] = -1
        subset['cluster_str'] = 'N/A'

    my_age_group_clustered.append(subset)

my_age_group_clustered_result = pd.concat(my_age_group_clustered)

# better visualization of scatterplot
age_group_labels = {
    '0': '18–24',
    '1': '25–34',
    '2': '35–44',
    '3': '45–54',
    '4': '55–64',
    '5': '65+'
}
my_age_group_clustered_result['age_group_label'] = my_age_group_clustered_result['age_group'].map(age_group_labels)
# dummy data for age groups without entry
all_age_groups = ['18–24', '25–34', '35–44', '45–54', '55–64', '65+']
existing_groups = my_age_group_clustered_result['age_group_label'].unique().tolist()
missing_groups = [g for g in all_age_groups if g not in existing_groups]
dummy_data = pd.DataFrame([{
    'client_id': None,
    'transaction_count': 0,
    'total_value': 0,
    'average_value': 0,
    'age_group_label': g,
    'cluster': -1,
    'cluster_str': 'N/A'
} for g in missing_groups])
my_age_group_clustered_result = pd.concat([my_age_group_clustered_result, dummy_data], ignore_index=True)

"""
Logic
"""
# Callback
@callback(
    Output(ID.CLUSTER_GRAPH, 'figure'),
    Output(ID.CLUSTER_LEGEND, 'children'),
    Output(ID.CLUSTER_DEFAULT_SWITCH_CONTAINER, 'style'),
    Input(ID.CLUSTER_DROPDOWN, 'value'),
    Input(ID.CLUSTER_DEFAULT_SWITCH, 'value')
)
def update_cluster(value, default_switch_value):
    # color scheme
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
    # Default
    if value == "Default":
        default_switch_container = {'display' : 'block'}
        if default_switch_value == 'total_value':
            fig = px.scatter(my_transactions_agg, x="transaction_count", y="total_value",
                            color="cluster_str",
                            color_discrete_map=cluster_colors,
                            hover_data=['client_id', 'transaction_count', 'total_value','average_value'],
                            title='Cluster: transaction amount/total value')
            fig.update_layout(showlegend=False)
        elif default_switch_value == 'average_value':
            fig = px.scatter(my_transactions_agg, x="transaction_count", y="average_value",
                             color="cluster_str",
                             color_discrete_map=cluster_colors,
                             hover_data=['client_id', 'transaction_count', 'total_value', 'average_value'],
                             title='Cluster: transaction amount/average value')
            fig.update_layout(showlegend=False)
        else:
            fig=px.scatter()
        legend = get_legend_default(cluster_colors)
    elif value == "Test":
        default_switch_container = {'display' : 'none'}
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
        legend = html.Ul([
            html.Li(f"Cluster {i}", style={"color": cluster_colors[str(i)]})
            for i in range(4)
        ])
    # Age Group
    elif value == "Age Group":
        default_switch_container = {'display' : 'block'}
        if default_switch_value == 'total_value':
            fig = px.scatter(my_age_group_clustered_result,
                             x="transaction_count",
                             y="total_value",
                             color="cluster_str",
                             color_discrete_map=cluster_colors,
                             facet_col="age_group_label",
                             facet_col_wrap=3,
                             category_orders={"age_group_label": ["18–24", "25–34", "35–44", "45–54", "55–64", "65+"]},
                             labels={"age_group_label": " "},
                             hover_data=["client_id", "total_value", "average_value"],
                             title="Cluster per age group total value")
            # removes '=' from scatterplot
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(showlegend=False)
        elif default_switch_value == 'average_value':
            fig = px.scatter(my_age_group_clustered_result,
                             x="transaction_count",
                             y="average_value",
                             color="cluster_str",
                             color_discrete_map=cluster_colors,
                             facet_col="age_group_label",
                             facet_col_wrap=3,
                             category_orders={"age_group_label": ["18–24", "25–34", "35–44", "45–54", "55–64", "65+"]},
                             hover_data=["client_id", "total_value", "average_value"],
                             title="Cluster per age group average value")
            # removes '=' from scatterplot
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(showlegend=False)
        else:
            fig = px.scatter()
        legend = get_legend_age_group(cluster_colors)
    elif value == "Income vs Expenditures":
        default_switch_container = {'display' : 'none'}
        fig = px.scatter()
        legend = get_legend_income_expenditure(cluster_colors)
    # in case something went wrong
    else:
        default_switch_container = {'display' : 'none'}
        fig = px.scatter()
        legend = html.Div("no legend available")
    return fig, html.Div([html.H5("Legend:"),html.Br(), legend]), default_switch_container

def get_legend_default(cluster_colors):
    legend = html.Ul([
        html.Li([
            html.Span("Cluster 0", style={"color": cluster_colors["0"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Few, low-value transactions", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),

        html.Li([
            html.Span("Cluster 1", style={"color": cluster_colors["1"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Frequent transactions with moderate amounts", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),

        html.Li([
            html.Span("Cluster 2", style={"color": cluster_colors["2"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Few but very large transactions", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),

        html.Li([
            html.Span("Cluster 3", style={"color": cluster_colors["3"], "font-weight": "bold"}),
            html.Br(),
            html.Span("High frequency and high value", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),
    ])
    return legend

def get_legend_age_group(cluster_colors):
    legend_items = [
        html.Li([
            html.Span("Cluster 0", style={"color": cluster_colors["0"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Few, low-value transactions", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),
        html.Li([
            html.Span("Cluster 1", style={"color": cluster_colors["1"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Frequent transactions with moderate amounts", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),
        html.Li([
            html.Span("Cluster 2", style={"color": cluster_colors["2"], "font-weight": "bold"}),
            html.Br(),
            html.Span("Few but very large transactions", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),
        html.Li([
            html.Span("Cluster 3", style={"color": cluster_colors["3"], "font-weight": "bold"}),
            html.Br(),
            html.Span("High frequency and high value", style={"color": "#555"}),
        ], style={"margin-bottom": "12px"}),
    ]
    # adds text for missing age groups
    if missing_groups:
        legend_items.append(html.Li([
            html.Span("no data for following age groups:", style={"font-weight": "bold", "color": "red"}),
            html.Br(),
            html.Span(", ".join(missing_groups), style={"color": "red"}),
        ], style={"margin-top": "20px"}))

    return html.Ul(legend_items)

def get_legend_income_expenditure(cluster_colors):
    legend = html.Ul([
        html.Li("Low Income / High Spending", style={"color": "red"}),
        html.Li("Low Income / Low Spending", style={"color": "blue"}),
        html.Li("High Income / High Spending", style={"color": "green"}),
        html.Li("High Income / Low Spending", style={"color": "yellow"}),
    ])
    return legend
