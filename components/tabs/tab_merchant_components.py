import pandas as pd
import plotly.graph_objects as go

import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager

dm: DataManager = DataManager.get_instance()
merchant_data = dm.merchant_tab_data


def create_merchant_group_line_chart(merchant_group):
    """
    Creates a line chart for a merchant group, displaying:
    - The number of transactions per day (left Y-axis)
    - The total transaction value per day (right Y-axis)

    Dual Y-axes are used to accommodate the typically different magnitudes
    of transaction count and total value, making both trends visible.

    Parameters:
    ----------
    merchant_group : str
        The merchant group identifier to filter transactions.

    Returns:
    -------
    plotly.graph_objects.Figure
        A Plotly figure object showing daily transaction count and value.
    """
    my_df = merchant_data.get_my_transactions_mcc_users()
    my_df = my_df[my_df['merchant_group'] == merchant_group].copy()
    if my_df.empty:
        return comp_factory.create_empty_figure()

    my_df['date'] = pd.to_datetime(my_df['date'])
    my_df['date_only'] = my_df['date'].dt.normalize()

    my_grouped = my_df.groupby('date_only').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    start_date = my_grouped['date_only'].min()
    end_date = my_grouped['date_only'].max()

    fig = go.Figure()

    # Primary Y-axis: transaction count
    fig.add_trace(go.Scatter(
        x=my_grouped['date_only'],
        y=my_grouped['transaction_count'],
        name='Transaction Count',
        yaxis='y1',
        line=dict(color='blue')
    ))

    # Secondary Y-axis: total value
    fig.add_trace(go.Scatter(
        x=my_grouped['date_only'],
        y=my_grouped['total_value'],
        name='Total Value',
        yaxis='y2',
        line=dict(color='red')
    ))

    fig.update_layout(
        # title=f"Transaction for Merchant Group: {merchant_group}",
        xaxis=dict(
            title='Date',
            range=[start_date, end_date]
        ),
        yaxis=dict(
            title=dict(text='Transaction Count', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Total Value', font=dict(color='red')),
            tickfont=dict(color='red'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig


def create_individual_merchant_line_chart(merchant):
    """
    Creates a line chart for a specific merchant, displaying:
    - The number of transactions per day (left Y-axis)
    - The total transaction value per day (right Y-axis)

    This dual-axis layout is used to visualize metrics with different scales
    simultaneously without losing granularity in the smaller values.

    Parameters:
    ----------
    merchant : str
        The unique merchant ID to filter the transactions dataset.

    Returns:
    -------
    plotly.graph_objects.Figure
        A Plotly figure object containing the time series chart with dual Y-axes.
    """
    my_df = merchant_data.get_my_transactions_mcc_users()
    my_df = my_df[my_df['merchant_id'] == merchant].copy()
    if my_df.empty:
        return comp_factory.create_empty_figure()

    my_df['date'] = pd.to_datetime(my_df['date'])
    my_df['date_only'] = my_df['date'].dt.normalize()

    my_grouped = my_df.groupby('date_only').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    start_date = my_grouped['date_only'].min()
    end_date = my_grouped['date_only'].max()

    fig = go.Figure()

    # Add transaction count to primary y-axis
    fig.add_trace(go.Scatter(
        x=my_grouped['date_only'],
        y=my_grouped['transaction_count'],
        name='Transaction Count',
        yaxis='y1',
        line=dict(color='blue')
    ))

    # Add total value to secondary y-axis
    fig.add_trace(go.Scatter(
        x=my_grouped['date_only'],
        y=my_grouped['total_value'],
        name='Total Value',
        yaxis='y2',
        line=dict(color='red')
    ))

    fig.update_layout(
        # title=f"Transaction for Merchant: {merchant}",
        xaxis=dict(
            title='Date',
            range=[start_date, end_date]
        ),
        yaxis=dict(
            title=dict(text='Transaction Count', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Total Value', font=dict(color='red')),
            tickfont=dict(color='red'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig
