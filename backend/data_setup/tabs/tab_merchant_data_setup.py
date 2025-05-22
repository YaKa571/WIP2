import pandas as pd
from backend.data_manager import DataManager
from backend.data_setup.tabs.tab_cluster_data_setup import prepare_default_data
import json
"""
contains data setup for Merchant tab
"""

# Data Files
dm: DataManager = DataManager.get_instance()
my_transactions = dm.df_transactions
# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
my_mcc["mcc"] = my_mcc["mcc"].astype(int)
# print(my_mcc.head())
# join transactions and mcc_codes
my_transactions_mcc=my_transactions.merge(my_mcc, how="left", on="mcc")

my_transactions_mcc_agg = my_transactions_mcc.groupby('merchant_group').agg(
    transaction_count=('merchant_group','count')
).reset_index()

my_transactions_agg_by_user = prepare_default_data(my_transactions)

def get_merchant_group_overview(threshold):
    """
        Aggregates merchant groups by transaction count, grouping smaller groups into 'Other'.

        This function takes a threshold value and separates merchant groups into "large" groups
        (with transaction counts greater than or equal to the threshold) and "small" groups
        (with counts below the threshold). It then sums the transaction counts of all small
        groups and adds them as a single 'Other' group to the large groups if the sum is greater than zero.

        Args:
            threshold (int): The minimum transaction count for a merchant group to be considered "large".

        Returns:
            pandas.DataFrame: A DataFrame containing merchant groups with transaction counts,
                              where groups below the threshold are combined into an 'Other' group.
                              The DataFrame has columns 'merchant_group' and 'transaction_count'.
        """
    my_df = my_transactions_mcc_agg.copy()
    large_groups = my_df[my_df['transaction_count'] >= threshold]
    small_groups = my_df[my_df['transaction_count'] < threshold]
    other_sum = small_groups['transaction_count'].sum()
    if other_sum > 0:
        other_df = pd.DataFrame([{
            'merchant_group': 'Other',
            'transaction_count': other_sum
        }])
        large_groups = pd.concat([large_groups, other_df], ignore_index=True)
    return large_groups

# TODO: calculation
def get_most_user_with_most_transactions_all_merchants():
    my_transactions_agg_by_user = prepare_default_data(my_transactions)
    my_transactions_agg_by_user = my_transactions_agg_by_user.reset_index().sort_values(by='transaction_count',
                                                                                        ascending=False)

    group_return = my_transactions_agg_by_user.loc[0, "client_id"]
    count_return = my_transactions_agg_by_user.loc[0, "transaction_count"]
    return group_return, count_return

# TODO: calculation
def get_user_with_highest_expenditure_all_merchants():
    my_transactions_agg_by_user = prepare_default_data(my_transactions)
    my_transactions_agg_by_user = my_transactions_agg_by_user.reset_index().sort_values(by='total_value',
                                                                                        ascending=False)

    group_return = my_transactions_agg_by_user.loc[0, "client_id"]
    count_return = my_transactions_agg_by_user.loc[0, "total_value"]
    return group_return, count_return

def get_most_frequently_used_merchant_group():
    """
        Calculate the merchant group with the highest number of transactions.

        This function counts how many transactions are associated with each merchant group
        by using the 'merchant_group' column in the DataFrame 'my_transactions_mcc'.
        It returns the merchant group that appears most frequently along with the count of transactions.

        Returns:
            tuple: (group_return, count_return)
                group_return (str): The name of the most frequently used merchant group.
                count_return (int): The number of transactions for this merchant group.
        """
    my_freq_agg = my_transactions_mcc["merchant_group"].value_counts()
    my_freq = my_freq_agg.reset_index().sort_values(by="count", ascending=False)
    group_return = my_freq.loc[0,"merchant_group"]
    count_return = my_freq.loc[0,"count"]
    return group_return, count_return

def get_highest_value_merchant_group():
    """
       Calculate the merchant group with the highest total transaction value.

       This function sums the 'amount' values for each merchant group in the DataFrame 'my_transactions_mcc'.
       It returns the merchant group with the highest aggregated transaction amount along with the total value.

       Returns:
           tuple: (group_return, value_return)
               group_return (str): The name of the merchant group with the highest transaction value.
               value_return (float): The total summed transaction amount for this merchant group.
       """
    my_value_agg = my_transactions_mcc.groupby("merchant_group")["amount"].sum()
    my_value = my_value_agg.reset_index().sort_values(by="amount", ascending=False)
    group_return = my_value.loc[0, "merchant_group"]
    value_return = my_value.loc[0, "amount"]
    return group_return, value_return
