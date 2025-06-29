from typing import Dict, Tuple, Optional
import datetime
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
        self.transactions_mcc_agg_by_state = None
        self.transactions_agg_by_user_and_state = None

        # Caches
        self._cache_merchant_group_overview = {}
        self._cache_all_merchant_groups = None
        self._cache_most_transactions_all_merchants: dict[Optional[str], tuple[int, int]] = {}
        self._cache_highest_expenditure_all_merchants: dict[Optional[str], tuple[int, float]] = {}
        self._cache_most_frequently_used_merchant_group: dict[Optional[str], tuple[str, int]] = {}
        self._cache_highest_value_merchant_group: dict[Optional[str], tuple[str, float]] = {}
        self._cache_most_frequently_used_merchant_in_group: Dict[Tuple[str, Optional[str]], Tuple[int, int]] = {}
        self._cache_highest_value_merchant_in_group: Dict[Tuple[str, Optional[str]], Tuple[int, float]] = {}
        self._cache_user_with_most_transactions_in_group: dict[tuple[str, Optional[str]], tuple[int, int]] = {}
        self._cache_user_with_highest_expenditure_in_group: dict[tuple[str, Optional[str]], tuple[int, float]] = {}
        self._cache_merchant_transactions: Dict[Tuple[int, Optional[str]], int] = {}
        self._cache_merchant_value: Dict[Tuple[int, Optional[str]], float] = {}
        self._cache_user_with_most_transactions_at_merchant: dict[tuple[int, Optional[str]], tuple[int, int]] = {}
        self._cache_user_with_highest_expenditure_at_merchant: dict[tuple[int, Optional[str]], tuple[int, float]] = {}
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

    def get_merchant_group_overview(self, threshold, state: Optional[str] = None):
        """
        Retrieves an overview of merchant groups with transaction counts based on a threshold
        and optional state filter. The result is cached to improve performance for repeated
        queries with the same parameters.

        Args:
            threshold (int): Minimum transaction count to categorize a merchant group as
                significant. Merchant groups with transaction counts below this threshold
                may be aggregated into an 'OTHER' category if necessary.
            state (Optional[str]): Optional filter for transactions by state. If provided, only
                transactions within the specified state are considered.

        Returns:
            pd.DataFrame: A DataFrame containing merchant groups and their corresponding
                transaction counts. Includes an 'OTHER' category if smaller groups are
                aggregated.
        """
        # Create cache key (tuple of threshold and state)
        cache_key = (threshold, state)
        if cache_key in self._cache_merchant_group_overview:
            return self._cache_merchant_group_overview[cache_key]

        # Select appropriate data source
        if state is not None:
            df = self.transactions_mcc_agg_by_state
            df = df[df["state_name"] == state].copy()
            df.drop(columns=["state_name"], inplace=True)
        else:
            df = self.transactions_mcc_agg.copy()

        # Sort by transaction count descending
        df = df.sort_values(by="transaction_count", ascending=False).reset_index(drop=True)

        # Apply threshold logic
        large_groups = df[df["transaction_count"] >= threshold]
        small_groups = df[df["transaction_count"] < threshold]

        # Ensure at least 10 groups remain (adjust threshold dynamically)
        if len(large_groups) < 10 and not small_groups.empty:
            num_needed = 10 - len(large_groups)
            extra = small_groups.head(num_needed)
            large_groups = pd.concat([large_groups, extra], ignore_index=True)
            small_groups = small_groups.iloc[num_needed:]

        # Add 'OTHER' category if remaining small groups exist
        if not small_groups.empty:
            other_sum = small_groups["transaction_count"].sum()
            other_row = pd.DataFrame([{
                "merchant_group": "OTHER",
                "transaction_count": other_sum
            }])
            large_groups = pd.concat([large_groups, other_row], ignore_index=True)

        # Cache and return
        self._cache_merchant_group_overview[cache_key] = large_groups
        return large_groups

    def get_user_with_most_transactions_all_merchants(self, state: str = None):
        """
        Retrieves the user with the highest number of transactions across all merchants. The user and
        their transaction count are fetched either across all states or filtered by a specific state.
        Results are cached to speed up subsequent queries.

        Args:
            state: The state name to filter transactions by. If None, considers transactions
                across all states.

        Returns:
            Tuple[int, int]: A tuple containing the user ID with the highest number of
            transactions and the corresponding transaction count. If the data is empty,
            returns (-1, 0).
        """
        # Check cache
        if state in self._cache_most_transactions_all_merchants:
            return self._cache_most_transactions_all_merchants[state]

        # Select appropriate DataFrame
        if state is None:
            df = self.transactions_agg_by_user
        else:
            df = self.transactions_agg_by_user_and_state
            df = df[df["state_name"] == state]

        if df.empty:
            result = (-1, 0)
        else:
            top_row = df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row["client_id"]), int(top_row["transaction_count"]))

        # Cache result
        self._cache_most_transactions_all_merchants[state] = result
        return result

    def get_user_with_highest_expenditure_all_merchants(self, state: str = None):
        """
        Retrieves the user with the highest expenditure across all merchants, optionally
        filtered by a specific state. Caches the result for future queries to improve
        performance.

        Args:
            state (str, optional): The name of the state to filter the search by. If
                None, considers all states. Defaults to None.

        Returns:
            tuple: A tuple containing the client ID (int) and their total expenditure
                (float). Returns (-1, 0.0) if no data is available for the given state
                or if the DataFrame is empty.
        """
        # Check cache
        if state in self._cache_highest_expenditure_all_merchants:
            return self._cache_highest_expenditure_all_merchants[state]

        # Select appropriate DataFrame
        if state is None:
            df = self.transactions_agg_by_user
        else:
            df = self.transactions_agg_by_user_and_state
            df = df[df["state_name"] == state]

        if df.empty:
            result = (-1, 0.0)
        else:
            top_row = df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row["client_id"]), float(top_row["total_value"]))

        # Cache result
        self._cache_highest_expenditure_all_merchants[state] = result
        return result

    def get_most_frequently_used_merchant_group(self, state: str = None):
        """
        Determines the most frequently used merchant group from transaction data
        for a specified state. If a state is not specified, the calculation uses
        data for all states.

        The method utilizes a cache to store results for previously computed states
        to optimize performance.

        Args:
            state (str, optional): The name of the state for which the most frequently
                used merchant group will be calculated. Defaults to None.

        Returns:
            tuple: A tuple containing the most frequently used merchant group as a
                string and its count as an integer. If the filtered data is empty, it
                returns ("UNKNOWN", 0).
        """
        # Check cache
        if state in self._cache_most_frequently_used_merchant_group:
            return self._cache_most_frequently_used_merchant_group[state]

        # Filter data by state if provided
        df = self.transactions_mcc
        if state:
            df = df[df["state_name"] == state]
        # Calculate
        if df.empty:
            result = ("UNKNOWN", 0)
        else:
            freq = (
                df.groupby("merchant_group")
                .size()
                .reset_index(name="count")
                .sort_values(by="count", ascending=False)
            )
            result = (freq.iloc[0]["merchant_group"], freq.iloc[0]["count"])

        # Cache & return
        self._cache_most_frequently_used_merchant_group[state] = result
        return result

    def get_highest_value_merchant_group(self, state: str = None):
        """Retrieves the merchant group with the highest total transaction value for a
        given state or overall if no state is specified. Caches the result for faster
        retrieval in subsequent calls.

        Args:
            state (str, optional): The name of the state for which to find the merchant
                group with the highest total transaction value. If None, calculations
                will be done using all available data.

        Returns:
            tuple[str, float]: A tuple where the first element is the name of the
                merchant group with the highest total transaction value and the second
                element is the corresponding total transaction value.
        """
        # Check cache
        if state in self._cache_highest_value_merchant_group:
            return self._cache_highest_value_merchant_group[state]

        # Filter data by state if provided
        df = self.transactions_mcc
        if state:
            df = df[df["state_name"] == state]

        # Calculate
        if df.empty:
            result = ("UNKNOWN", 0.0)
        else:
            value = (
                df.groupby("merchant_group")["amount"]
                .sum()
                .reset_index()
                .sort_values(by="amount", ascending=False)
            )
            result = (value.iloc[0]["merchant_group"], value.iloc[0]["amount"])

        # Cache & return
        self._cache_highest_value_merchant_group[state] = result
        return result

    def get_most_frequently_used_merchant_in_group(self, merchant_group, state: str = None):
        """
        Gets the most frequently used merchant in a specified merchant group. If a state
        is provided, the search is filtered within that state. The result is cached to
        optimize subsequent calls with the same parameters.

        Args:
            merchant_group: The identifier of the merchant group for which the most
                frequently used merchant is to be determined.
            state: Optional; the state name to filter the transactions within a
                specific region.

        Returns:
            Tuple[int, int]: A tuple containing the merchant ID of the most frequently
            used merchant and its transaction count. Returns (-1, -1) if there are no
            transactions matching the criteria.
        """
        # Check cache
        cache_key = (merchant_group, state)
        if cache_key in self._cache_most_frequently_used_merchant_in_group:
            return self._cache_most_frequently_used_merchant_in_group[cache_key]

        # Filter
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        if state:
            df = df[df["state_name"] == state]

        # Compute
        agg_df = df.groupby('merchant_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['merchant_id']), int(top_row['transaction_count']))

        # Cache
        self._cache_most_frequently_used_merchant_in_group[cache_key] = result
        return result

    def get_highest_value_merchant_in_group(self, merchant_group, state: str = None):
        """
        Finds the merchant with the highest transaction value within a specified merchant
        group, optionally filtered by state.

        This function calculates the merchant with the highest total transaction amount
        for a given merchant group. Optionally, if a state is provided, the calculation
        will consider only transactions within the specified state. The result is cached
        to optimize repeated calls with the same parameters.

        Args:
            merchant_group: The merchant group for which the analysis should be performed.
            state: The name of the state to filter transactions by. Defaults to None.

        Returns:
            A tuple containing:
                - An integer representing the ID of the highest value merchant.
                - A float representing the total transaction value of this merchant.
        """
        # Check cache
        cache_key = (merchant_group, state)
        if cache_key in self._cache_highest_value_merchant_in_group:
            return self._cache_highest_value_merchant_in_group[cache_key]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        if state:
            df = df[df["state_name"] == state]

        if df.empty:
            result = (-1, 0.0)
        else:
            agg_df = df.groupby('merchant_id')['amount'].sum().reset_index()
            top_row = agg_df.sort_values(by='amount', ascending=False).iloc[0]
            result = (int(top_row['merchant_id']), float(top_row['amount']))

        # Cache result
        self._cache_highest_value_merchant_in_group[cache_key] = result
        return result

    def get_user_with_most_transactions_in_group(self, merchant_group, state: str = None):
        """
        Retrieves the user with the most transactions within a specified merchant group,
        and optionally filters by state. The result is cached for subsequent queries
        with identical merchant group and state.

        Args:
            merchant_group: Merchant group for which the transactions are queried.
            state: Optional; State by which to filter transactions.

        Returns:
            Tuple[int, int]: A tuple containing the client ID of the user with the most
            transactions and the corresponding transaction count. Returns (-1, -1) if
            there are no transactions matching the criteria.
        """
        # Check cache
        cache_key = (merchant_group, state)
        if cache_key in self._cache_user_with_most_transactions_in_group:
            return self._cache_user_with_most_transactions_in_group[cache_key]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        if state:
            df = df[df['state_name'] == state]

        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['client_id']), int(top_row['transaction_count']))

        # Cache result
        self._cache_user_with_most_transactions_in_group[cache_key] = result
        return result

    def get_user_with_highest_expenditure_in_group(self, merchant_group, state: str = None):
        """
        Retrieves the user with the highest expenditure within a specified merchant group and
        optionally within a specified state. This method utilizes a caching mechanism to store
        the results of previous calculations and optimize performance.

        The calculation is performed by filtering transaction data for the given merchant group
        and state (if provided), then aggregating the expenditure data by client ID to determine
        the user with the highest total expenditure.

        Args:
            merchant_group: The merchant group for which the user with the highest expenditure
                is to be determined.
            state: An optional parameter representing the state within which the calculation
                should be performed. If not specified, calculations are done for all states.

        Returns:
            A tuple containing two elements:
                - The client ID of the user with the highest expenditure. If the data set is empty,
                  returns -1.
                - The total expenditure value associated with the highest-spending user. If the
                  data set is empty, returns -1.0.
        """
        # Check cache
        cache_key = (merchant_group, state)
        if cache_key in self._cache_user_with_highest_expenditure_in_group:
            return self._cache_user_with_highest_expenditure_in_group[cache_key]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_group'] == merchant_group]
        if state:
            df = df[df['state_name'] == state]

        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            result = (-1, -1)
        else:
            top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row['client_id']), float(top_row['total_value']))

        # Cache result
        self._cache_user_with_highest_expenditure_in_group[cache_key] = result
        return result

    def get_merchant_transactions(self, merchant, state: str = None):
        """
        Gets the number of transactions associated with a given merchant, optionally
        filtered by state. If the result is already available in the cache, it retrieves
        the value from the cache. Otherwise, it calculates the count and stores it in
        the cache for future requests.

        Args:
            merchant: Identifier of the merchant for which transactions are being queried.
            state (str, optional): State name to filter transactions. If not provided,
                transactions are not filtered by state.

        Returns:
            int: The number of transactions associated with the given merchant, optionally
                filtered by state.
        """
        # Check cache
        cache_key = (merchant, state)
        if cache_key in self._cache_merchant_transactions:
            return self._cache_merchant_transactions[cache_key]

        # Calculate
        df = self.transactions_mcc_users
        if state:
            df = df[df["state_name"] == state]

        count = df[df["merchant_id"] == merchant].shape[0]

        # Cache result
        self._cache_merchant_transactions[cache_key] = count
        return count

    def get_merchant_value(self, merchant, state: str = None):
        """
        Calculates and retrieves the total transaction value for a specific merchant, optionally
        filtering by state. Uses an internal caching mechanism to reduce redundant calculations.

        Args:
            merchant: The identifier of the merchant for which to calculate the total transaction value.
            state: Optional; the name of the state to filter the transactions by before calculation.

        Returns:
            float: The total transaction value for the given merchant, filtered by state if specified.
        """
        # Check cache
        cache_key = (merchant, state)
        if cache_key in self._cache_merchant_value:
            return self._cache_merchant_value[cache_key]

        # Calculate
        df = self.transactions_mcc_users
        if state:
            df = df[df["state_name"] == state]

        total_value = df[df["merchant_id"] == merchant]["amount"].sum()

        # Cache result
        self._cache_merchant_value[cache_key] = total_value
        return total_value

    def get_user_with_most_transactions_at_merchant(self, merchant, state: str = None):
        """
        Finds the user with the most transactions at a given merchant, optionally filtered by state.

        This method analyzes transaction data to determine the client with the highest number
        of transactions for a specific merchant. If a state is provided, it filters the data
        to include only transactions within that state. Results are cached to improve
        performance for subsequent calls with the same parameters.

        Args:
            merchant: ID of the merchant for whom the transactions should be analyzed.
            state: Optional; name of the state to filter transactions.

        Returns:
            A tuple of two integers:
            - The client ID of the user with the most transactions.
            - The count of transactions made by that user.
            If no transactions are found, (-2, -2) is returned.
        """
        # Check cache
        cache_key = (merchant, state)
        if cache_key in self._cache_user_with_most_transactions_at_merchant:
            return self._cache_user_with_most_transactions_at_merchant[cache_key]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        if state:
            df = df[df['state_name'] == state]

        agg_df = df.groupby('client_id').size().reset_index(name='transaction_count')
        if agg_df.empty:
            result = (-2, -2)
        else:
            top_row = agg_df.sort_values(by='transaction_count', ascending=False).iloc[0]
            result = (int(top_row['client_id']), int(top_row['transaction_count']))

        # Cache result
        self._cache_user_with_most_transactions_at_merchant[cache_key] = result
        return result

    def get_user_with_highest_expenditure_at_merchant(self, merchant, state: str = None):
        """
        Fetches the user with the highest expenditure at a specified merchant, optionally filtered
        by state, and caches the result.

        This method processes transaction data to calculate the total expenditure of each user
        for the specified merchant. If a state is provided, the data is filtered for transactions
        matching the specified state. The user with the highest expenditure is identified, and
        their client ID along with their total expenditure is returned. Results are cached to
        optimize future calls with the same inputs.

        Args:
            merchant: Identifier for the merchant whose transactions are to be analyzed.
            state: Optional; The state filter to limit the analysis to a specific geographic location.

        Returns:
            tuple: A tuple containing the client ID (int) of the user with the highest expenditure
            at the specified merchant and the total amount spent (float). If there are no matching
            transactions, returns a tuple (-2, -2).
        """
        # Check cache
        cache_key = (merchant, state)
        if cache_key in self._cache_user_with_highest_expenditure_at_merchant:
            return self._cache_user_with_highest_expenditure_at_merchant[cache_key]

        # Calculate
        df = self.transactions_mcc_users[self.transactions_mcc_users['merchant_id'] == merchant]
        if state:
            df = df[df['state_name'] == state]

        agg_df = df.groupby('client_id')['amount'].sum().reset_index(name='total_value')
        if agg_df.empty:
            result = (-2, -2)
        else:
            top_row = agg_df.sort_values(by='total_value', ascending=False).iloc[0]
            result = (int(top_row['client_id']), float(top_row['total_value']))

        # Cache result
        self._cache_user_with_highest_expenditure_at_merchant[cache_key] = result
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
        Pre-caches data for merchant-related tabs in the system. This involves loading
        caches from disk if available or generating intermediary and top-level caches
        for merchant and merchant group data based on various filters, including user
        transactions, expenditures, and thresholds. The function leverages concurrent
        processing to optimize the pre-cache process.

        Args:
            log_times (bool): Indicates whether to log the benchmarking times of each
                caching stage. Defaults to True.
        """
        import concurrent.futures

        logger.log("🔄 Merchant: Pre-caching Merchant Tab data...", indent_level=3)
        bm_pre_cache_full = Benchmark("Merchant: Pre-caching Merchant Tab data")

        # Try to load caches from disk first
        if self._load_caches_from_disk():
            logger.log("✅ Merchant: Successfully loaded caches from disk", indent_level=3)
            bm_pre_cache_full.print_time(level=4)
            return

        # Get all relevant states
        all_states = self.transactions_mcc_users["state_name"].dropna().unique().tolist()
        all_states.append(None)  # also pre-cache unfiltered version
        logger.log(f"ℹ️ Merchant: Found {len(all_states)-1} states plus overall aggregation", indent_level=4)

        # Cache global data (no parameters)
        logger.log("🔄 Merchant: Pre-caching global merchant data...", indent_level=4)
        bm_global = Benchmark("Merchant: Pre-caching global merchant data")
        self.get_all_merchant_groups()

        logger.log("🔄 Merchant: Pre-caching user and merchant group metrics for all states...", indent_level=4)

        # Define a function to process global metrics for a single state
        def process_global_metrics_for_state(state):
            state_name = state if state else "All States"
            logger.log(f"🔄 Merchant: Processing global metrics for state: {state_name}", indent_level=5, debug=True)
            self.get_user_with_most_transactions_all_merchants(state)
            self.get_user_with_highest_expenditure_all_merchants(state)
            self.get_most_frequently_used_merchant_group(state)
            self.get_highest_value_merchant_group(state)
            for threshold in [10, 20, 50]:
                self.get_merchant_group_overview(threshold, state)
            return state

        # Process global metrics for all states in parallel
        with concurrent.futures.ThreadPoolExecutor() as global_executor:
            # Submit all tasks
            global_futures = [global_executor.submit(process_global_metrics_for_state, state) for state in all_states]

            # Wait for all tasks to complete
            global_results = [future.result() for future in concurrent.futures.as_completed(global_futures)]

        logger.log(f"✅ Merchant: Global merchant data pre-caching completed for {len(global_results)} states", indent_level=4)
        bm_global.print_time(level=4)

        # Define merchant group cache function with state
        def cache_merchant_group_data(group):
            logger.log(f"🔄 Merchant: Pre-caching data for merchant group: '{group}'", indent_level=5, debug=True)

            # Define a function to process a single state for this merchant group
            def process_state_for_group(state):
                state_name = state if state else "All States"
                logger.log(f"🔄 Merchant: Processing group '{group}' in {state_name}", indent_level=6, debug=True)
                self.get_most_frequently_used_merchant_in_group(group, state)
                self.get_highest_value_merchant_in_group(group, state)
                self.get_user_with_most_transactions_in_group(group, state)
                self.get_user_with_highest_expenditure_in_group(group, state)
                return state

            # Process all states for this merchant group in parallel
            with concurrent.futures.ThreadPoolExecutor() as group_state_executor:
                # Submit all tasks
                state_futures = [group_state_executor.submit(process_state_for_group, state) for state in all_states]

                # Wait for all tasks to complete
                state_results = [future.result() for future in concurrent.futures.as_completed(state_futures)]

            return group

        # Define merchant cache function with state
        def cache_merchant_data(merchant):
            logger.log(f"🔄 Merchant: Pre-caching data for merchant ID: {merchant}", indent_level=5, debug=True)

            # Define a function to process a single state for this merchant
            def process_state_for_merchant(state):
                state_name = state if state else "All States"
                logger.log(f"🔄 Merchant: Processing merchant {merchant} in {state_name}", indent_level=6, debug=True)
                self.get_merchant_transactions(merchant, state)
                self.get_merchant_value(merchant, state)
                self.get_user_with_most_transactions_at_merchant(merchant, state)
                self.get_user_with_highest_expenditure_at_merchant(merchant, state)
                return state

            # Process all states for this merchant in parallel
            with concurrent.futures.ThreadPoolExecutor() as merchant_state_executor:
                # Submit all tasks
                state_futures = [merchant_state_executor.submit(process_state_for_merchant, state) for state in all_states]

                # Wait for all tasks to complete
                state_results = [future.result() for future in concurrent.futures.as_completed(state_futures)]

            return merchant

        merchant_groups = self.get_all_merchant_groups()
        logger.log(f"ℹ️ Merchant: Found {len(merchant_groups)} merchant groups to process", indent_level=4)

        logger.log("🔄 Merchant: Identifying top merchants...", indent_level=4)
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
        logger.log(f"ℹ️ Merchant: Selected top {len(top_merchants)} merchants for pre-caching", indent_level=4)
        bm_merchants.print_time(level=4)

        # Track progress for merchant groups
        total_groups = len(merchant_groups)
        completed_groups = 0

        # Define a callback function to update progress
        def group_completed(future):
            nonlocal completed_groups
            completed_groups += 1
            percentage = (completed_groups / total_groups) * 100
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.log(f"ℹ️ Merchant: Progress for merchant groups: {completed_groups}/{total_groups} ({percentage:.1f}%) [{current_time}]", indent_level=4)

        # Track progress for top merchants
        total_merchants = len(top_merchants)
        completed_merchants = 0

        # Define a callback function to update progress
        def merchant_completed(future):
            nonlocal completed_merchants
            completed_merchants += 1
            percentage = (completed_merchants / total_merchants) * 100
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.log(f"ℹ️ Merchant: Progress for top merchants: {completed_merchants}/{total_merchants} ({percentage:.1f}%) [{current_time}]", indent_level=4)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            logger.log("🔄 Merchant: Starting parallel pre-caching for all merchant groups...", indent_level=4)
            bm_groups = Benchmark("Merchant: Pre-caching data for all merchant groups")

            # Submit all tasks and add callbacks for progress tracking
            futures_groups = []
            for group in merchant_groups:
                future = executor.submit(cache_merchant_group_data, group)
                future.add_done_callback(group_completed)
                futures_groups.append(future)

            # Wait for all tasks to complete
            results_groups = [future.result() for future in concurrent.futures.as_completed(futures_groups)]
            logger.log(f"✅ Merchant: Successfully pre-cached data for {len(results_groups)} merchant groups", indent_level=4)
            bm_groups.print_time(level=4)

            logger.log("🔄 Merchant: Starting parallel pre-caching for top merchants...", indent_level=4)
            bm_merchants = Benchmark("Merchant: Pre-caching data for top merchants")

            # Submit all tasks and add callbacks for progress tracking
            futures_merchants = []
            for merchant in top_merchants:
                future = executor.submit(cache_merchant_data, merchant)
                future.add_done_callback(merchant_completed)
                futures_merchants.append(future)

            # Wait for all tasks to complete
            results_merchants = [future.result() for future in concurrent.futures.as_completed(futures_merchants)]
            logger.log(f"✅ Merchant: Successfully pre-cached data for {len(results_merchants)} top merchants", indent_level=4)
            bm_merchants.print_time(level=4)

        logger.log("💾 Merchant: Saving all cached data to disk...", indent_level=4)
        self._save_caches_to_disk()
        logger.log("✅ Merchant: Pre-caching completed successfully", indent_level=3)
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
        # Aggregate by merchant group AND state
        self.transactions_mcc_agg_by_state = (
            self.transactions_mcc
            .groupby(['state_name', 'merchant_group'], sort=False)
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

        # Aggregate by user AND state
        self.transactions_agg_by_user_and_state = (
            self.df_transactions
            .groupby(['state_name', 'client_id'], sort=False)
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
