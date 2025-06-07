import pandas as pd
import plotly.express as px



def fraud_by_state_bar(merged_df: pd.DataFrame):
    """
    Creates a bar chart showing the number of transactions per US state.
    Helps identify where most fraudulent activity occurs geographically.
    """
    state_counts = merged_df['merchant_state'].value_counts().reset_index()
    state_counts.columns = ['merchant_state', 'transaction_count']

    fig = px.bar(
        state_counts,
        x='merchant_state',
        y='transaction_count',
        title='Transactions per U.S. State',
        labels={'merchant_state': 'State', 'transaction_count': 'Transaction Count'}
    )
    return fig


def online_transaction_share_pie(merged_df: pd.DataFrame):
    """
    Creates a pie chart showing the proportion of online vs. physical transactions.
    Uses merchant_city to determine online activity.
    """
    df = merged_df.copy()  
    df['is_online'] = df['merchant_city'].isna() | (df['merchant_city'].str.lower() == 'online')
    counts = df['is_online'].value_counts().rename({True: 'Online', False: 'In-store'}).reset_index()
    counts.columns = ['type', 'count']

    fig = px.pie(
        counts,
        names='type',
        values='count',
        title='Share of Online vs. In-Store Transactions'
    )
    return fig


def top_online_merchants(merged_df: pd.DataFrame):
    """
    Displays the top 10 merchant IDs with the most online transactions.
    Useful for detecting suspiciously active merchants online.
    """
    online_df = merged_df[merged_df['merchant_city'].isna() | (merged_df['merchant_city'].str.lower() == 'online')]
    top_merchants = online_df['merchant_id'].value_counts().nlargest(10).reset_index()
    top_merchants.columns = ['merchant_id', 'transaction_count']

    fig = px.bar(
        top_merchants,
        x='merchant_id',
        y='transaction_count',
        title='Top 10 Online Merchant IDs',
        labels={'merchant_id': 'Merchant ID', 'transaction_count': 'Transaction Count'}
    )
    return fig


