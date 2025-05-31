import pandas as pd
import plotly.graph_objects as go

import components.constants as const
import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager

dm: DataManager = DataManager.get_instance()
merchant_data = dm.merchant_tab_data


def create_merchant_group_line_chart(merchant_group, dark_mode: bool = const.DEFAULT_DARK_MODE):
    """
    Creates a line chart for a merchant group, displaying:
    - The number of transactions per day (left Y-axis)
    - The total transaction value per day (right Y-axis)

    Dual Y-axes are used to accommodate the typically different magnitudes
    of transaction count and total value, making both trends visible.
    The chart adapts to dark mode when enabled.

    Parameters:
    ----------
    merchant_group : str
        The merchant group identifier to filter transactions.
    dark_mode : bool, optional
        Whether to use dark mode styling. Defaults to False.

    Returns:
    -------
    plotly.graph_objects.Figure
        A Plotly figure object showing daily transaction count and value.
    """
    df = merchant_data.get_my_transactions_mcc_users()
    df = df[df['merchant_group'] == merchant_group].copy()
    if df.empty:
        return comp_factory.create_empty_figure()

    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.normalize()

    df_grouped = df.groupby('date_only').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    start_date = df_grouped['date_only'].min()
    end_date = df_grouped['date_only'].max()

    fig = go.Figure()

    # Primary Y-axis: transaction count
    fig.add_trace(go.Scatter(
        x=df_grouped['date_only'],
        y=df_grouped['transaction_count'],
        name='TRANSACTION COUNT',
        yaxis='y1',
        line=dict(color=const.COLOR_BLUE_MAIN)
    ))

    # Secondary Y-axis: total value
    fig.add_trace(go.Scatter(
        x=df_grouped['date_only'],
        y=df_grouped['total_value'],
        name='TOTAL VALUE',
        yaxis='y2',
        line=dict(color='red')
    ))

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    fig.update_layout(
        font=dict(color=text_color),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        xaxis=dict(
            title='DATE',
            range=[start_date, end_date],
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        yaxis=dict(
            title=dict(text='TRANSACTION COUNT', font=dict(color=const.COLOR_BLUE_MAIN)),
            tickfont=dict(color=const.COLOR_BLUE_MAIN),
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        yaxis2=dict(
            title=dict(text='TOTAL VALUE', font=dict(color='red')),
            tickfont=dict(color='red'),
            anchor='x',
            overlaying='y',
            side='right',
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        legend=dict(x=0.5, y=0.975, xanchor='center', yanchor='top'),
        margin=dict(l=1, r=1, t=1, b=1)
    )

    return fig


def create_individual_merchant_line_chart(merchant, dark_mode: bool = const.DEFAULT_DARK_MODE):
    """
    Creates a line chart for a specific merchant, displaying:
    - The number of transactions per day (left Y-axis)
    - The total transaction value per day (right Y-axis)

    This dual-axis layout is used to visualize metrics with different scales
    simultaneously without losing granularity in the smaller values.
    The chart adapts to dark mode when enabled.

    Parameters:
    ----------
    merchant : str
        The unique merchant ID to filter the transactions dataset.
    dark_mode : bool, optional
        Whether to use dark mode styling. Defaults to False.

    Returns:
    -------
    plotly.graph_objects.Figure
        A Plotly figure object containing the time series chart with dual Y-axes.
    """

    show_spinner_cls = "map-spinner visible"
    hide_spinner_cls = "map-spinner"

    df = merchant_data.get_my_transactions_mcc_users()
    df = df[df['merchant_id'] == merchant].copy()
    if df.empty:
        return comp_factory.create_empty_figure(), show_spinner_cls

    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.normalize()

    df_grouped = df.groupby('date_only').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    start_date = df_grouped['date_only'].min()
    end_date = df_grouped['date_only'].max()

    fig = go.Figure()

    # Add transaction count to primary y-axis
    fig.add_trace(go.Scatter(
        x=df_grouped['date_only'],
        y=df_grouped['transaction_count'],
        name='TRANSACTION COUNT',
        yaxis='y1',
        line=dict(color=const.COLOR_BLUE_MAIN)
    ))

    # Add total value to secondary y-axis
    fig.add_trace(go.Scatter(
        x=df_grouped['date_only'],
        y=df_grouped['total_value'],
        name='TOTAL VALUE',
        yaxis='y2',
        line=dict(color='red')
    ))

    # Set colors based on dark mode
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    fig.update_layout(
        # title=f"Transaction for Merchant: {merchant}",
        font=dict(color=text_color),
        plot_bgcolor=const.COLOR_TRANSPARENT,
        paper_bgcolor=const.COLOR_TRANSPARENT,
        xaxis=dict(
            title='DATE',
            range=[start_date, end_date],
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        yaxis=dict(
            title=dict(text='TRANSACTION COUNT', font=dict(color=const.COLOR_BLUE_MAIN)),
            tickfont=dict(color=const.COLOR_BLUE_MAIN),
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        yaxis2=dict(
            title=dict(text='TOTAL VALUE', font=dict(color='red')),
            tickfont=dict(color='red'),
            anchor='x',
            overlaying='y',
            side='right',
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        legend=dict(x=0.5, y=0.975, xanchor='center', yanchor='top'),
        margin=dict(l=1, r=1, t=1, b=1)
    )

    return fig, hide_spinner_cls
