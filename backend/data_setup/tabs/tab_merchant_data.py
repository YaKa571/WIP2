import json

import pandas as pd

from utils import logger
from utils.benchmark import Benchmark


class MerchantTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users
        self.mcc_dict = data_manager.mcc_dict

        # Initialize dataframes
        self.mcc = None
        self.transactions_mcc = None
        self.transactions_mcc_agg = None
        self.transactions_agg_by_user = None
        self.transactions_mcc_users = None

        # Caches
        self._cache_merchant_group_overview = {}

    def initialize(self):
        """
        Initialize the merchant tab data by loading and processing the necessary data.
        """
        logger.log("ℹ️ Initializing Merchant Tab Data...", 2)
        bm = Benchmark("Initialization")

        # Load MCC codes
        with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
        self.mcc["mcc"] = self.mcc["mcc"].astype(int)

        # Join transactions and mcc_codes
        self.transactions_mcc = self.df_transactions.merge(self.mcc, how="left", on="mcc")

        # Aggregate by merchant group
        self.transactions_mcc_agg = self.transactions_mcc.groupby('merchant_group').agg(
            transaction_count=('merchant_group', 'count')
        ).reset_index()

        # Aggregate by user
        self.transactions_agg_by_user = self.df_transactions.groupby('client_id').agg(
            transaction_count=('amount', 'count'),
            total_value=('amount', 'sum')
        ).reset_index()

        # Transactions join MCC join Users
        self.transactions_mcc_users = self.transactions_mcc.merge(
            self.df_users, how="left", left_on='client_id', right_on='id'
        )

        bm.print_time(level=3)

    def get_my_transactions_mcc_users(self):
        """
        Returns the merged dataframe of transactions, MCC codes, and user data.
        
        Returns:
            pandas.DataFrame: The merged dataframe.
        """
        return self.transactions_mcc_users

    def get_all_merchant_groups(self):
        """
        Returns a sorted list of all unique merchant groups.
        
        Returns:
            list: A sorted list of all unique merchant groups.
        """
        return sorted(self.mcc['merchant_group'].unique().tolist())

    def get_merchant_group_overview(self, threshold):
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
        # Check cache
        if threshold in self._cache_merchant_group_overview:
            return self._cache_merchant_group_overview[threshold]

        df = self.transactions_mcc_agg.copy()
        large_groups = df[df['transaction_count'] >= threshold]
        small_groups = df[df['transaction_count'] < threshold]
        other_sum = small_groups['transaction_count'].sum()
        if other_sum > 0:
            other_df = pd.DataFrame([{
                'merchant_group': 'OTHER',
                'transaction_count': other_sum
            }])
            large_groups = pd.concat([large_groups, other_df], ignore_index=True)

        # Cache result
        self._cache_merchant_group_overview[threshold] = large_groups
        return large_groups

    def get_most_user_with_most_transactions_all_merchants(self):
        """
        Identify the user with the highest number of transactions across all merchant groups.

        This function sorts the transaction data aggregated by user in descending order
        based on transaction count, then selects the user with the most transactions.

        Returns:
            tuple: (user_id, transaction_count)
                user_id (int): ID of the user with the most transactions.
                transaction_count (int): Number of transactions made by this user.
        """
        df = self.transactions_agg_by_user.reset_index().sort_values(by='transaction_count',
                                                                     ascending=False)

        user_return = int(df.iloc[0]["client_id"])
        count_return = int(df.iloc[0]["transaction_count"])
        return user_return, count_return

    def get_user_with_highest_expenditure_all_merchants(self):
        """
        Identify the user with the highest total expenditure across all merchant groups.

        This function sorts the transaction data aggregated by user in descending order
        based on total transaction value, then selects the user with the highest spending.

        Returns:
            tuple: (user_id, total_value)
                user_id (int): ID of the user with the highest total expenditure.
                total_value (float): Sum of all transaction amounts by this user.
        """
        df = self.transactions_agg_by_user.reset_index().sort_values(by='total_value', ascending=False)

        user_return = int(df.iloc[0]["client_id"])
        value_return = df.iloc[0]["total_value"]
        return user_return, value_return

    def get_most_frequently_used_merchant_group(self):
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
        freq_agg = self.transactions_mcc["merchant_group"].value_counts()
        freq = freq_agg.reset_index().sort_values(by="count", ascending=False)
        group_return = freq.loc[0, "merchant_group"]
        count_return = freq.loc[0, "count"]
        return group_return, count_return

    def get_highest_value_merchant_group(self):
        """
        Calculate the merchant group with the highest total transaction value.

        This function sums the 'amount' values for each merchant group in the DataFrame 'my_transactions_mcc'.
        It returns the merchant group with the highest aggregated transaction amount along with the total value.

        Returns:
            tuple: (group_return, value_return)
                group_return (str): The name of the merchant group with the highest transaction value.
                value_return (float): The total summed transaction amount for this merchant group.
        """
        value_agg = self.transactions_mcc.groupby("merchant_group")["amount"].sum()
        value = value_agg.reset_index().sort_values(by="amount", ascending=False)
        group_return = value.loc[0, "merchant_group"]
        value_return = value.loc[0, "amount"]
        return group_return, value_return

    def get_most_frequently_used_merchant_in_group(self, merchant_group):
        """
        Find the merchant within the specified merchant group with the highest number of transactions.

        Args:
            merchant_group (str): The name of the merchant group.

        Returns:
            tuple: (merchant_id, transaction_count)
                merchant_id (int): ID of the merchant with the most transactions.
                transaction_count (int): Number of transactions for this merchant.
                Returns (-1, -1) if no transactions exist for the group.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('merchant_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            return -1, -1
        top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
        return int(top_row['merchant_id']), int(top_row['transaction_count'])

    def get_highest_value_merchant_in_group(self, merchant_group):
        """
        Find the merchant within the specified merchant group with the highest total transaction value.

        Args:
            merchant_group (str): The name of the merchant group.

        Returns:
            tuple: (merchant_id, total_value)
                merchant_id (int): ID of the merchant with the highest total transaction amount.
                total_value (float): Sum of transaction amounts for this merchant.
                Returns (-1, -1) if no transactions exist for the group.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('merchant_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            return -1, -1
        top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
        return int(top_row['merchant_id']), float(top_row['total_value'])

    def get_user_with_most_transactions_in_group(self, merchant_group):
        """
        Identify the user with the most transactions within the specified merchant group.

        Args:
            merchant_group (str): The name of the merchant group.

        Returns:
            tuple: (client_id, transaction_count)
                client_id (int): ID of the user with the most transactions.
                transaction_count (int): Number of transactions by this user.
                Returns (-1, -1) if no transactions exist for the group.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            return -1, -1
        top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
        return int(top_row['client_id']), int(top_row['transaction_count'])

    def get_user_with_highest_expenditure_in_group(self, merchant_group):
        """
        Identify the user with the highest total expenditure within the specified merchant group.

        Args:
            merchant_group (str): The name of the merchant group.

        Returns:
            tuple: (client_id, total_value)
                client_id (int): ID of the user with the highest total spending.
                total_value (float): Sum of all transaction amounts by this user.
                Returns (-1, -1) if no transactions exist for the group.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            return -1, -1
        top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
        return int(top_row['client_id']), float(top_row['total_value'])

    def get_merchant_transactions(self, merchant):
        """
        Calculate the total number of transactions for a given merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            int: The number of transactions for this merchant.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        return len(df)

    def get_merchant_value(self, merchant):
        """
        Calculate the total transaction value for a given merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            float: The sum of all transaction amounts for this merchant.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        return df['amount'].sum()

    def get_user_with_most_transactions_at_merchant(self, merchant):
        """
        Identify the user with the most transactions at a specific merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            tuple: (client_id, transaction_count)
                client_id (int): ID of the user with the most transactions at this merchant.
                transaction_count (int): Number of transactions by this user.
                Returns (-2, -2) if no transactions exist for this merchant.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            return -2, -2
        top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
        return int(top_row['client_id']), int(top_row['transaction_count'])

    def get_user_with_highest_expenditure_at_merchant(self, merchant):
        """
        Identify the user with the highest total expenditure at a specific merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            tuple: (client_id, total_value)
                client_id (int): ID of the user with the highest spending at this merchant.
                total_value (float): Sum of all transaction amounts by this user.
                Returns (-2, -2) if no transactions exist for this merchant.
        """
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            return -2, -2
        top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
        return int(top_row['client_id']), float(top_row['total_value'])
