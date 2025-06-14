import pandas as pd
import plotly.graph_objects as go

import components.constants as const
import components.factories.component_factory as comp_factory
from backend.data_manager import DataManager

dm: DataManager = DataManager.get_instance()
merchant_data = dm.merchant_tab_data


def create_merchant_group_line_chart(merchant_group, state: str = None, dark_mode: bool = const.DEFAULT_DARK_MODE):
    """
    Generates a line chart displaying transaction count and total value over time for a specific merchant
    group. The chart features dual axes to represent transaction count and total value, and is
    customized based on user preferences like state and display mode (dark or light theme).
    The chart adapts to varying time periods and handles scenarios with no data gracefully.

    Args:
        merchant_group: Name of the merchant group for which the line chart is generated.
        state: Optional; filter to transactions within a specific state. Default is None.
        dark_mode: Determines if the chart should be rendered in dark mode. Defaults to the global
            setting in `const.DEFAULT_DARK_MODE`.

    Returns:
        Figure object: A Plotly figure representing the generated line chart.
    """
    df = merchant_data.get_my_transactions_mcc_users()

    # Apply filters
    df = df[df['merchant_group'] == merchant_group]
    if state is not None and 'state_name' in df.columns:
        df = df[df['state_name'] == state]

    df = df.copy() # prevents warning

    if df.empty:
        return comp_factory.create_empty_figure()

    # Convert and normalize date
    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.normalize()

    # Aggregate
    df_grouped = df.groupby('date_only').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    # Axis bounds
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
        line=dict(color=const.COLOR_ORANGE)
    ))

    # Theme colors
    text_color = const.TEXT_COLOR_DARK if dark_mode else const.TEXT_COLOR_LIGHT
    grid_color = const.GRAPH_GRID_COLOR_DARK if dark_mode else const.GRAPH_GRID_COLOR_LIGHT

    # Layout
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
            title=dict(text='TOTAL VALUE', font=dict(color=const.COLOR_ORANGE)),
            tickfont=dict(color=const.COLOR_ORANGE),
            anchor='x',
            overlaying='y',
            side='right',
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        legend=dict(x=0.5, y=1, xanchor='center', yanchor='top'),
        margin=dict(l=1, r=1, t=1, b=1)
    )

    return fig


def create_individual_merchant_line_chart(merchant,state=None,dark_mode: bool = const.DEFAULT_DARK_MODE):
    """
    Creates an individual line chart for a specified merchant's transactions over time. The function
    processes transaction data, aggregates metrics, and visualizes them in an interactive plotly
    graph, enabling dual-axis comparison of transaction count and total value across a date range.

    Args:
        merchant: The identifier of the merchant for which the chart is created.
        state: Optional filter specifying the state of transactions to be included. Defaults to None.
        dark_mode: Indicates if the chart should use a dark mode color scheme. Defaults to
            const.DEFAULT_DARK_MODE.

    Returns:
        tuple: A plotly `Figure` object representing the line chart and a spinner class string. The
            spinner class corresponds to the visibility state of a spinner element.
    """
    show_spinner_cls = "map-spinner visible"
    hide_spinner_cls = "map-spinner"

    df = merchant_data.get_my_transactions_mcc_users()
    df = df[df['merchant_id'] == merchant]

    if state is not None and 'state_name' in df.columns:
        df = df[df['state_name'] == state]

    df = df.copy()  # prevents warning

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
        line=dict(color=const.COLOR_ORANGE)
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
            title=dict(text='TOTAL VALUE', font=dict(color=const.COLOR_ORANGE)),
            tickfont=dict(color=const.COLOR_ORANGE),
            anchor='x',
            overlaying='y',
            side='right',
            gridcolor=grid_color,
            zerolinecolor=grid_color
        ),
        legend=dict(x=0.5, y=1, xanchor='center', yanchor='top'),
        margin=dict(l=1, r=1, t=1, b=1)
    )

    return fig, hide_spinner_cls
