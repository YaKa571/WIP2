from typing import Dict, Tuple

import pandas as pd

from utils import logger
from utils.benchmark import Benchmark


class MerchantTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users
        self.df_mcc = data_manager.df_mcc

        # Initialize dataframes
        self.mcc = None
        self.transactions_mcc = None
        self.transactions_mcc_agg = None
        self.transactions_agg_by_user = None
        self.transactions_mcc_users = None

        # Caches
        self._cache_merchant_group_overview = {}
        self._cache_all_merchant_groups = None
        self._cache_most_transactions_all_merchants = None
        self._cache_highest_expenditure_all_merchants = None
        self._cache_most_frequently_used_merchant_group = None
        self._cache_highest_value_merchant_group = None
        self._cache_most_frequently_used_merchant_in_group: Dict[str, Tuple[int, int]] = {}
        self._cache_highest_value_merchant_in_group: Dict[str, Tuple[int, float]] = {}
        self._cache_user_with_most_transactions_in_group: Dict[str, Tuple[int, int]] = {}
        self._cache_user_with_highest_expenditure_in_group: Dict[str, Tuple[int, float]] = {}
        self._cache_merchant_transactions: Dict[int, int] = {}
        self._cache_merchant_value: Dict[int, float] = {}
        self._cache_user_with_most_transactions_at_merchant: Dict[int, Tuple[int, int]] = {}
        self._cache_user_with_highest_expenditure_at_merchant: Dict[int, Tuple[int, float]] = {}
        self.unique_merchant_ids = set(self.df_transactions["merchant_id"].unique())

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
        # Check cache
        if self._cache_all_merchant_groups is not None:
            return self._cache_all_merchant_groups

        # Calculate and cache
        result = sorted(self.mcc['merchant_group'].unique().tolist())
        self._cache_all_merchant_groups = result
        return result

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

    def get_user_with_most_transactions_all_merchants(self):
        """
        Identify the user with the highest number of transactions across all merchant groups.

        This function sorts the transaction data aggregated by user in descending order
        based on transaction count, then selects the user with the most transactions.

        Returns:
            tuple: (user_id, transaction_count)
                user_id (int): ID of the user with the most transactions.
                transaction_count (int): Number of transactions made by this user.
        """
        # Check cache
        if self._cache_most_transactions_all_merchants is not None:
            return self._cache_most_transactions_all_merchants

        # Calculate
        df = self.transactions_agg_by_user.reset_index().sort_values(by='transaction_count',
                                                                     ascending=False)

        user_return = int(df.iloc[0]["client_id"])
        count_return = int(df.iloc[0]["transaction_count"])

        # Cache result
        self._cache_most_transactions_all_merchants = (user_return, count_return)
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
        # Check cache
        if self._cache_highest_expenditure_all_merchants is not None:
            return self._cache_highest_expenditure_all_merchants

        # Calculate
        df = self.transactions_agg_by_user.reset_index().sort_values(by='total_value', ascending=False)

        user_return = int(df.iloc[0]["client_id"])
        value_return = df.iloc[0]["total_value"]

        # Cache result
        self._cache_highest_expenditure_all_merchants = (user_return, value_return)
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
        # Check cache
        if self._cache_most_frequently_used_merchant_group is not None:
            return self._cache_most_frequently_used_merchant_group

        # Calculate
        freq_agg = self.transactions_mcc["merchant_group"].value_counts()
        freq = freq_agg.reset_index().sort_values(by="count", ascending=False)
        group_return = freq.loc[0, "merchant_group"]
        count_return = freq.loc[0, "count"]

        # Cache result
        self._cache_most_frequently_used_merchant_group = (group_return, count_return)
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
        # Check cache
        if self._cache_highest_value_merchant_group is not None:
            return self._cache_highest_value_merchant_group

        # Calculate
        value_agg = self.transactions_mcc.groupby("merchant_group")["amount"].sum()
        value = value_agg.reset_index().sort_values(by="amount", ascending=False)
        group_return = value.loc[0, "merchant_group"]
        value_return = value.loc[0, "amount"]

        # Cache result
        self._cache_highest_value_merchant_group = (group_return, value_return)
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
        # Check cache
        if merchant_group in self._cache_most_frequently_used_merchant_in_group:
            return self._cache_most_frequently_used_merchant_in_group[merchant_group]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('merchant_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['merchant_id']), int(top_row['transaction_count']))

        # Cache result
        self._cache_most_frequently_used_merchant_in_group[merchant_group] = result
        return result

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
        # Check cache
        if merchant_group in self._cache_highest_value_merchant_in_group:
            return self._cache_highest_value_merchant_in_group[merchant_group]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('merchant_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row['merchant_id']), float(top_row['total_value']))

        # Cache result
        self._cache_highest_value_merchant_in_group[merchant_group] = result
        return result

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
        # Check cache
        if merchant_group in self._cache_user_with_most_transactions_in_group:
            return self._cache_user_with_most_transactions_in_group[merchant_group]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['client_id']), int(top_row['transaction_count']))

        # Cache result
        self._cache_user_with_most_transactions_in_group[merchant_group] = result
        return result

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
        # Check cache
        if merchant_group in self._cache_user_with_highest_expenditure_in_group:
            return self._cache_user_with_highest_expenditure_in_group[merchant_group]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row['client_id']), float(top_row['total_value']))

        # Cache result
        self._cache_user_with_highest_expenditure_in_group[merchant_group] = result
        return result

    def get_merchant_transactions(self, merchant):
        """
        Calculate the total number of transactions for a given merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            int: The number of transactions for this merchant.
        """
        # Check cache
        if merchant in self._cache_merchant_transactions:
            return self._cache_merchant_transactions[merchant]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        result = len(df)

        # Cache result
        self._cache_merchant_transactions[merchant] = result
        return result

    def get_merchant_value(self, merchant):
        """
        Calculate the total transaction value for a given merchant.

        Args:
            merchant (int): The merchant ID.

        Returns:
            float: The sum of all transaction amounts for this merchant.
        """
        # Check cache
        if merchant in self._cache_merchant_value:
            return self._cache_merchant_value[merchant]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        result = df['amount'].sum()

        # Cache result
        self._cache_merchant_value[merchant] = result
        return result

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
        # Check cache
        if merchant in self._cache_user_with_most_transactions_at_merchant:
            return self._cache_user_with_most_transactions_at_merchant[merchant]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-2, -2)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['client_id']), int(top_row['transaction_count']))

        # Cache result
        self._cache_user_with_most_transactions_at_merchant[merchant] = result
        return result

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
        # Check cache
        if merchant in self._cache_user_with_highest_expenditure_at_merchant:
            return self._cache_user_with_highest_expenditure_at_merchant[merchant]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            result = (-2, -2)
        else:
            top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row['client_id']), float(top_row['total_value']))

        # Cache result
        self._cache_user_with_highest_expenditure_at_merchant[merchant] = result
        return result

    def _save_caches_to_disk(self):
        """
        Save all cached data to disk.
        """
        logger.log("🔄 Merchant: Saving caches to disk...", indent_level=3)
        bm = Benchmark("Merchant: Saving caches to disk")

        # Save all cache dictionaries
        cache_data = {
            "merchant_group_overview": self._cache_merchant_group_overview,
            "all_merchant_groups": self._cache_all_merchant_groups,
            "most_transactions_all_merchants": self._cache_most_transactions_all_merchants,
            "highest_expenditure_all_merchants": self._cache_highest_expenditure_all_merchants,
            "most_frequently_used_merchant_group": self._cache_most_frequently_used_merchant_group,
            "highest_value_merchant_group": self._cache_highest_value_merchant_group,
            "most_frequently_used_merchant_in_group": self._cache_most_frequently_used_merchant_in_group,
            "highest_value_merchant_in_group": self._cache_highest_value_merchant_in_group,
            "user_with_most_transactions_in_group": self._cache_user_with_most_transactions_in_group,
            "user_with_highest_expenditure_in_group": self._cache_user_with_highest_expenditure_in_group,
            "merchant_transactions": self._cache_merchant_transactions,
            "merchant_value": self._cache_merchant_value,
            "user_with_most_transactions_at_merchant": self._cache_user_with_most_transactions_at_merchant,
            "user_with_highest_expenditure_at_merchant": self._cache_user_with_highest_expenditure_at_merchant
        }

        self.data_manager.save_cache_to_disk("merchant_tab_caches", cache_data)
        bm.print_time(level=4)

    def _load_caches_from_disk(self) -> bool:
        """
        Load all cached data from disk.

        Returns:
            bool: True if caches were successfully loaded, False otherwise
        """
        logger.log("🔄 Merchant: Loading caches from disk...", indent_level=3)
        bm = Benchmark("Merchant: Loading caches from disk")

        # Load cache dictionaries
        cache_data = self.data_manager.load_cache_from_disk("merchant_tab_caches", is_dataframe=False)
        if cache_data is not None:
            self._cache_merchant_group_overview = cache_data.get("merchant_group_overview", {})
            self._cache_all_merchant_groups = cache_data.get("all_merchant_groups")
            self._cache_most_transactions_all_merchants = cache_data.get("most_transactions_all_merchants")
            self._cache_highest_expenditure_all_merchants = cache_data.get("highest_expenditure_all_merchants")
            self._cache_most_frequently_used_merchant_group = cache_data.get("most_frequently_used_merchant_group")
            self._cache_highest_value_merchant_group = cache_data.get("highest_value_merchant_group")
            self._cache_most_frequently_used_merchant_in_group = cache_data.get("most_frequently_used_merchant_in_group", {})
            self._cache_highest_value_merchant_in_group = cache_data.get("highest_value_merchant_in_group", {})
            self._cache_user_with_most_transactions_in_group = cache_data.get("user_with_most_transactions_in_group", {})
            self._cache_user_with_highest_expenditure_in_group = cache_data.get("user_with_highest_expenditure_in_group", {})
            self._cache_merchant_transactions = cache_data.get("merchant_transactions", {})
            self._cache_merchant_value = cache_data.get("merchant_value", {})
            self._cache_user_with_most_transactions_at_merchant = cache_data.get("user_with_most_transactions_at_merchant", {})
            self._cache_user_with_highest_expenditure_at_merchant = cache_data.get("user_with_highest_expenditure_at_merchant", {})
            bm.print_time(level=4)
            return True

        bm.print_time(level=4)
        return False

    def _pre_cache_merchant_tab_data(self, log_times: bool = True) -> None:
        """
        Pre-caches data for the Merchant Tab view by performing data aggregation and calculations for
        merchant groups and merchants. This method is intended to optimize subsequent data retrieval
        and ensure that necessary insights are readily available for analysis.

        Parameters
        ----------
        log_times : bool, optional
            Whether to log the time taken for data processing. Defaults to True.

        Returns
        -------
        None
        """
        import concurrent.futures

        logger.log("🔄 Merchant: Pre-caching Merchant Tab data...", indent_level=3)
        bm_pre_cache_full = Benchmark("Merchant: Pre-caching Merchant Tab data")

        # Try to load caches from disk first
        if self._load_caches_from_disk():
            logger.log("✅ Merchant: Successfully loaded caches from disk", indent_level=3)
            bm_pre_cache_full.print_time(level=4)
            return

        # Cache global data (no parameters) - these are fast and dependencies for other caches
        bm_global = Benchmark("Merchant: Pre-caching global merchant data")
        self.get_all_merchant_groups()
        self.get_user_with_most_transactions_all_merchants()
        self.get_user_with_highest_expenditure_all_merchants()
        self.get_most_frequently_used_merchant_group()
        self.get_highest_value_merchant_group()

        # Cache merchant group overview with common thresholds
        thresholds = [10, 20, 50]
        for threshold in thresholds:
            self.get_merchant_group_overview(threshold)
        bm_global.print_time(level=4)

        # Define functions to cache data for a merchant group
        def cache_merchant_group_data(group):
            # Cache all data for this merchant group
            self.get_most_frequently_used_merchant_in_group(group)
            self.get_highest_value_merchant_in_group(group)
            self.get_user_with_most_transactions_in_group(group)
            self.get_user_with_highest_expenditure_in_group(group)
            return group

        # Define function to cache data for a merchant
        def cache_merchant_data(merchant):
            # Cache all data for this merchant
            self.get_merchant_transactions(merchant)
            self.get_merchant_value(merchant)
            self.get_user_with_most_transactions_at_merchant(merchant)
            self.get_user_with_highest_expenditure_at_merchant(merchant)
            return merchant

        # Get merchant groups and top merchants
        merchant_groups = self.get_all_merchant_groups()

        # Get top merchants more efficiently
        bm_merchants = Benchmark("Merchant: Identifying top merchants")
        merchant_counts = (
            self.transactions_mcc_users
            .groupby('merchant_id', sort=False)
            .size()
            .reset_index(name='count')
            .sort_values(by='count', ascending=False)
            .head(100)
        )
        top_merchants = merchant_counts['merchant_id'].tolist()
        bm_merchants.print_time(level=4)

        # Use ThreadPoolExecutor for parallel processing
        # This is ideal for I/O-bound operations like these caching operations
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Cache merchant group data in parallel
            bm_groups = Benchmark("Merchant: Pre-caching data for all merchant groups")
            list(executor.map(cache_merchant_group_data, merchant_groups))
            bm_groups.print_time(level=4)

            # Cache merchant data in parallel
            bm_merchants = Benchmark("Merchant: Pre-caching data for top merchants")
            list(executor.map(cache_merchant_data, top_merchants))
            bm_merchants.print_time(level=4)

        # Save caches to disk for future use
        self._save_caches_to_disk()

        bm_pre_cache_full.print_time(level=4)

    def initialize(self):
        """
        Initialize the merchant tab data by loading and processing the necessary data.
        """
        logger.log("ℹ️ Merchant: Initializing Merchant Tab Data...", 3, add_line_before=True)
        bm = Benchmark("Merchant: Initialization")

        # Use shared MCC codes from data manager
        self.mcc = self.data_manager.df_mcc

        # Use shared transactions_mcc from data manager
        self.transactions_mcc = self.data_manager.transactions_mcc

        # Aggregate by merchant group - use more efficient named aggregation
        self.transactions_mcc_agg = (
            self.transactions_mcc
            .groupby('merchant_group', sort=False)  # Avoid sorting for better performance
            .agg(transaction_count=('merchant_group', 'count'))
            .reset_index()
        )

        # Aggregate by user - use more efficient named aggregation
        self.transactions_agg_by_user = (
            self.df_transactions
            .groupby('client_id', sort=False)  # Avoid sorting for better performance
            .agg(
                transaction_count=('amount', 'count'),
                total_value=('amount', 'sum')
            )
            .reset_index()
        )

        # Use shared transactions_mcc_users from data manager
        self.transactions_mcc_users = self.data_manager.transactions_mcc_users

        # Pre-cache merchant data
        self._pre_cache_merchant_tab_data()

        bm.print_time(level=4, add_empty_line=True)
