import pandas as pd
import datetime
from sklearn.cluster import KMeans
"""
contains data setup for Cluster tab
"""
def get_age_group(age: int) -> str:
    """
    Assigns an age to an age group.

    Age groups:
        0: 18–24
        1: 25–34
        2: 35–44
        3: 45–54
        4: 55–64
        5: 65+

    Args:
        age (int): Age of the person.

    Returns:
        str: Age group label as a string ('0' to '5').
    """
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

def prepare_test_data() -> pd.DataFrame:
    """
    Prepares sample test data and applies KMeans clustering.

    Creates example transactions with client_id and amount.
    Aggregates transactions per client and performs clustering.

    Returns:
        pd.DataFrame: Aggregated test data with cluster assignment.
    """
    my_test_df = pd.DataFrame({
        'client_id': [1, 1, 2, 2, 3, 4, 4, 4, 5, 1, 1, 1, 6],
        'amount': [100, 150, 10, 20, 500, 5, 10, 15, 1000, 250, 4500, 30, 450]
    })
    my_test_agg = my_test_df.groupby('client_id').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    kmeans_default = KMeans(n_clusters=4, n_init=20)
    my_test_agg['cluster'] = kmeans_default.fit_predict(my_test_agg[['transaction_count', 'total_value']])
    my_test_agg['cluster_str'] = my_test_agg['cluster'].astype(str)  # For coloring in plots

    return my_test_agg

def prepare_default_data(my_transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates transactions by client and applies clustering.

    Calculates average transaction value and creates two cluster sets:
    one based on total_value, one based on average_value.

    Args:
        my_transactions (pd.DataFrame): Raw transaction data with 'client_id' and 'amount'.

    Returns:
        pd.DataFrame: Aggregated transaction data with cluster assignments.
    """
    my_transactions_agg = my_transactions.groupby('client_id').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum')
    ).reset_index()

    my_transactions_agg['average_value'] = my_transactions_agg['total_value'] / my_transactions_agg['transaction_count']

    # Clustering based on total_value
    kmeans_default_total = KMeans(n_clusters=4, random_state=42, n_init=30)
    my_transactions_agg['cluster'] = kmeans_default_total.fit_predict(my_transactions_agg[['transaction_count', 'total_value']])
    my_transactions_agg['cluster_str'] = my_transactions_agg['cluster'].astype(str)

    # Clustering based on average_value
    kmeans_default_avg = KMeans(n_clusters=4, random_state=42, n_init=30)
    my_transactions_agg['cluster_average'] = kmeans_default_avg.fit_predict(my_transactions_agg[['transaction_count', 'average_value']])
    my_transactions_agg['cluster_average_str'] = my_transactions_agg['cluster_average'].astype(str)

    return my_transactions_agg

def prepare_age_group_data(my_transactions: pd.DataFrame, my_users: pd.DataFrame) -> pd.DataFrame:
    """
    Joins transactions with user data, calculates age groups, and clusters per age group.

    Args:
        my_transactions (pd.DataFrame): Transaction data with 'client_id' and 'amount'.
        my_users (pd.DataFrame): User data with at least 'id' and 'birth_year'.

    Returns:
        pd.DataFrame: Aggregated and clustered transaction data with age groups.
    """
    # Join transactions with user data on client_id / id
    my_transactions_users_joined = my_transactions.merge(
        my_users,
        left_on='client_id',
        right_on='id',
        how='left'
    )

    # Calculate current age
    current_year = datetime.datetime.now().year
    my_transactions_users_joined['current_age'] = current_year - my_transactions_users_joined['birth_year']

    # Assign age groups
    my_transactions_users_joined['age_group'] = my_transactions_users_joined['current_age'].apply(get_age_group)

    # Aggregate per client: transaction count, total value, average value, and age group
    my_age_group = my_transactions_users_joined.groupby('client_id').agg(
        transaction_count=('amount', 'count'),
        total_value=('amount', 'sum'),
        average_value=('amount', 'mean'),
        age_group=('age_group', 'first')  # Client's age group (first occurrence)
    ).reset_index()

    # Perform clustering per age group
    my_age_group_clustered = []
    for group in my_age_group['age_group'].unique():
        subset = my_age_group[my_age_group['age_group'] == group].copy()

        if len(subset) >= 4:  # KMeans needs at least as many points as clusters
            kmeans_age_group = KMeans(n_clusters=4, random_state=42, n_init=30)
            subset['cluster'] = kmeans_age_group.fit_predict(subset[['transaction_count', 'total_value']])
            subset['cluster_str'] = subset['cluster'].astype(str)
        else:
            subset['cluster'] = -1
            subset['cluster_str'] = 'N/A'  # For groups with too few data points

        my_age_group_clustered.append(subset)

    # Combine results
    my_age_group_clustered_result = pd.concat(my_age_group_clustered)

    return my_age_group_clustered_result