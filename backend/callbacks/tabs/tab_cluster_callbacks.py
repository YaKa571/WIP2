import pandas as pd
import plotly.express as px
import datetime
from dash import Input, Output, callback, html
from sklearn.cluster import KMeans

from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_cluster_data_setup import prepare_test_data, prepare_default_data, \
    prepare_age_group_data
from frontend.component_ids import ID

"""
callbacks of tab cluster
"""

# Data Files
dm: DataManager = DataManager.get_instance()
my_transactions = dm.df_transactions
my_users = dm.df_users

my_test_agg = prepare_test_data()
my_transactions_agg = prepare_default_data(my_transactions)
my_age_group_clustered_result = prepare_age_group_data(my_transactions, my_users)
# Test Data File
my_test_df = pd.DataFrame({'client_id': [1, 1, 2, 2, 3, 4, 4, 4, 5, 1, 1, 1, 6],
                           'amount': [100, 150, 10, 20, 500, 5, 10, 15, 1000, 250, 4500, 30, 450]
                           })

"""
Additional Data and Scatterplot Set Up for Age Group
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
Callback
"""
@callback(
    Output(ID.CLUSTER_GRAPH, 'figure'),
    Output(ID.CLUSTER_LEGEND, 'children'),
    Output(ID.CLUSTER_DEFAULT_SWITCH_CONTAINER, 'style'),
    Input(ID.CLUSTER_DROPDOWN, 'value'),
    Input(ID.CLUSTER_DEFAULT_SWITCH, 'value')
)
def update_cluster(value, default_switch_value):
    """
        Update the cluster scatter plot figure, legend, and UI visibility based on user input.

        This callback function dynamically generates a scatter plot visualization of clustered transaction data,
        responding to user selections for clustering type ('Default', 'Test', 'Age Group', 'Income vs Expenditures')
        and a switch controlling whether to display total or average transaction values.

        Parameters:
            value (str): Selected cluster type from dropdown ('Default', 'Test', 'Age Group', 'Income vs Expenditures').
            default_switch_value (str): Selected value type for the default cluster ('total_value' or 'average_value').

        Returns:
            tuple:
                fig (plotly.graph_objs._figure.Figure): Scatter plot figure showing transaction clusters.
                legend (dash.html.Div): HTML component containing the legend describing clusters.
                default_switch_container (dict): CSS style dict controlling visibility of the default switch UI element.
        """
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
    """
        Generate the HTML legend for the default clustering view.

        Creates an unordered list (<ul>) of cluster descriptions with colored labels
        corresponding to cluster colors, explaining the characteristics of each cluster
        in terms of transaction frequency and value.

        Parameters:
            cluster_colors (dict): Mapping of cluster IDs (str) to color hex codes (str).

        Returns:
            dash.html.Ul: HTML unordered list component representing the cluster legend.
        """
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
    """
       Generate the HTML legend for clustering by age group.

       Builds a legend similar to the default legend, adding additional information
       if any age groups are missing from the clustered dataset.

       Parameters:
           cluster_colors (dict): Mapping of cluster IDs (str) to color hex codes (str).

       Returns:
           dash.html.Ul: HTML unordered list component representing the age group cluster legend.
       """
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
    # TODO
    legend = html.Ul([
        html.Li("Low Income / High Spending", style={"color": "red"}),
        html.Li("Low Income / Low Spending", style={"color": "blue"}),
        html.Li("High Income / High Spending", style={"color": "green"}),
        html.Li("High Income / Low Spending", style={"color": "yellow"}),
    ])
    return legend
