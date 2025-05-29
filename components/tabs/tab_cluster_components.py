import plotly.express as px
from dash import html

import components.constants as const
from backend.data_manager import DataManager

# Initialize DataManager instance
dm: DataManager = DataManager.get_instance()
cluster_data = dm.cluster_tab_data


def make_cluster_plot(df_agg, mode='total_value', age_group_mode='all', dark_mode: bool = False):
    """
    Generates a cluster plot visualizing transaction data segmented by cluster and other grouping parameters.

    This function creates a scatter plot using transaction data, where data points represent individual
    clients grouped by clusters. Clusters are visualized with different colors and symbols. The plot
    can optionally group data by age groups and supports customization for light and dark themes.

    Parameters:
        df_agg (DataFrame): Aggregated transaction data containing columns like 'transaction_count',
                            'total_value', 'average_value', and cluster information.
        mode (str, optional): Determines the y-axis metric ('total_value' or 'average_value'). Default is 'total_value'.
        age_group_mode (str, optional): Controls grouping by age groups. Available options are 'all' or 'grouped'.
                                        Default is 'all'.
        dark_mode (bool, optional): Toggles between dark and light modes for the plot. Default is False.

    Returns:
        Figure: A Plotly scatter plot figure object configured as per the input parameters.
    """
    cluster_column = 'cluster_total_str' if mode == 'total_value' else 'cluster_avg_str'
    y_column = 'total_value' if mode == 'total_value' else 'average_value'

    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    symbol_map = {
        'Cluster 0': 'circle',
        'Cluster 1': 'square',
        'Cluster 2': 'diamond',
        'Cluster 3': 'triangle-up'
    }

    fig = px.scatter(
        df_agg,
        x='transaction_count',
        y=y_column,
        color=cluster_column,
        color_discrete_map=cluster_data.get_cluster_colors(),
        symbol=cluster_column,
        symbol_map=symbol_map,
        opacity=0.8,
        size_max=10,
        hover_data={
            'client_id': True,
            'transaction_count': True,
            'total_value': ':.2f',
            'average_value': ':.2f',
            cluster_column: True,
            'age_group': True
        },
        title=f'CLUSTER PER AGE GROUP {"TOTAL VALUE" if mode == "total_value" else "AVERAGE VALUE"}',
        facet_col='age_group' if age_group_mode == 'grouped' else None,
        facet_col_wrap=3,
        category_orders={"age_group": ['<25', '26–35', '36–45', '46–55', '56–65', '65+']},
        labels={
            "transaction_count": "TRANSACTIONS",
            y_column: "TOTAL VALUE" if mode == "total_value" else "AVERAGE VALUE",
            "age_group": "AGE GROUP",
            cluster_column: "CLUSTER"
        }
    )

    fig.for_each_annotation(lambda a: a.update(
        text=f"<b>{a.text.split('=')[-1]}</b>",
        font=dict(size=15, color=text_color)
    ))

    fig.update_xaxes(
        showline=False,
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=grid_color,
    )
    fig.update_yaxes(
        showline=False,
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=grid_color,
    )

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        selector=dict(mode='markers')
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=32, r=32, t=56, b=32),
        title_x=0.5,
        title_y=0.97,
        font=dict(family="Open Sans, Arial, sans-serif", size=14, color=text_color),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
    )

    return fig


def create_cluster_legend(mode: str, df) -> list:
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
            color = cluster_data.get_cluster_colors().get(str(cl), "#000000")
            items.append(
                create_legend_item(color=color, text=f"{desc}")
            )

        else:
            # more detailed description, if description already exists
            clusters_sorted = sorted(clusters_with_desc, key=lambda c: means[c][0])
            base_desc = desc
            for i, cl in enumerate(clusters_sorted):
                color = cluster_data.get_cluster_colors().get(str(cl), "#000000")
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
                    create_legend_item(color=color, text=f"{desc}{suffix}")
                )

    return items


def make_inc_vs_exp_plot(df_agg, age_group_mode='all', dark_mode: bool = False):
    """
    Generates a scatter plot visualizing yearly income versus total expenses, segmented by clusters
    and optionally grouped by age groups, with customization options for dark mode. The function
    leverages Plotly to create an interactive, aesthetically customizable plot for exploratory data
    analysis.

    Parameters:
        df_agg: pandas.DataFrame
            The aggregated DataFrame containing client data including yearly income,
            total expenses, clusters, and optional age group information.
        age_group_mode: str, optional
            Specifies how age groups are handled in the plot. Acceptable values are
            'all' for no grouping or 'grouped' for facetting by age groups. Defaults to 'all'.
        dark_mode: bool, optional
            Determines whether the plot should use colors suitable for dark mode.
            Defaults to False.

    Returns:
        plotly.graph_objs._figure.Figure
            A Plotly scatter plot figure object visualizing income and expenses grouped
            by clusters, optionally facetted by age groups.
    """

    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    symbol_map = {
        'Cluster 0': 'circle',
        'Cluster 1': 'square',
        'Cluster 2': 'diamond',
        'Cluster 3': 'triangle-up'
    }

    fig = px.scatter(
        df_agg,
        x='yearly_income',
        y='total_expenses',
        color='cluster_inc_vs_exp_str',
        color_discrete_map=cluster_data.get_cluster_colors(),
        symbol='cluster_inc_vs_exp_str',
        symbol_map=symbol_map,
        opacity=0.8,
        size_max=10,
        hover_data=['client_id', 'yearly_income', 'total_expenses'],
        title='CLUSTER PER AGE GROUP INCOME VS EXPENSES',
        facet_col='age_group' if age_group_mode == 'grouped' else None,
        facet_col_wrap=3,
        category_orders={"age_group": ['<25', '26–35', '36–45', '46–55', '56–65', '65+']},
        labels={
            "yearly_income": "YEARLY INCOME",
            "total_expenses": "TOTAL EXPENSES",
            "age_group": "AGE GROUP",
            "cluster_inc_vs_exp_str": "CLUSTER"
        }
    )

    fig.for_each_annotation(lambda a: a.update(
        text=f"<b>{a.text.split('=')[-1]}</b>",
        font=dict(size=15, color=text_color)
    ))

    fig.update_xaxes(
        showline=False,
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=grid_color,
    )
    fig.update_yaxes(
        showline=False,
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color),
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        linecolor=grid_color,
    )

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        selector=dict(mode='markers')
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=32, r=32, t=56, b=32),
        title_x=0.5,
        title_y=0.97,
        font=dict(family="Open Sans, Arial, sans-serif", size=14, color=text_color),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
    )

    return fig


def create_legend_item(color: str, text: str, bold_text: str = None):
    """
    Creates a legend item that consists of a colored block and descriptive text.

    The function generates a styled HTML component containing a color indicator and
    two text elements: one bold and the other regular. It is used for visually
    representing the mapping between colors and their corresponding meanings in
    a legend.

    Args:
        color (str): The background color for the color block (e.g., a color code like "#FFFFFF").
        bold_text (str): The text to be displayed in bold, serving as a heading or
            label for the legend item.
        text (str): Additional descriptive text to follow the bold text.

    Returns:
        html.Div: An HTML component consisting of a styled color block and text
            information forming a legend item.
    """

    children = [
        html.Span(bold_text, style={"fontWeight": "bold"}),
        html.Br(),
        text
    ] if bold_text else text

    return html.Div(
        className="legend-item-wrapper",
        children=[

            html.Div(
                className="legend-color",
                style={
                    "backgroundColor": color,
                }
            ),

            html.Div(
                className="legend-text",
                children=children
            )

        ]
    )
