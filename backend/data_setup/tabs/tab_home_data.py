from typing import Optional, Callable, Any

import pandas as pd

from backend.data_handler import get_mcc_description_by_merchant_id
from backend.kpi_models import MerchantKPI, PeakHourKPI, UserKPI, VisitKPI
from utils import logger
from utils.benchmark import Benchmark


class HomeTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users
        self.df_cards = data_manager.df_cards
        self.df_mcc = data_manager.df_mcc

        # Caches
        self._cache_most_valuable_merchant: dict[str, pd.DataFrame] = {}
        self._cache_visits_by_merchant: dict[Optional[str], pd.DataFrame] = {}
        self._cache_spending_by_user: dict[Optional[str], pd.DataFrame] = {}
        self._cache_transaction_counts_by_hour: dict[Optional[str], pd.DataFrame] = {}
        self._cache_expenditures_by_gender: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_age: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_channel: dict[str | None, dict[str, float]] = {}
        self.map_data: pd.DataFrame = pd.DataFrame()

    def get_merchant_values_by_state(self, state: str = None) -> pd.DataFrame:
        """
        Fetches and processes merchant transaction data grouped by state and mcc.

        This method returns a DataFrame containing the aggregated transaction amount
        per merchant grouped by 'merchant_id' and 'mcc', sorted in descending order
        by total transaction amount. If a specific state is provided, the data is
        filtered for that state. Processed results are cached to enhance
        performance for repeated calls with the same state.

        Parameters:
        state: str, optional
            The state for which data needs to be fetched. If None, data for all states
            is processed.

        Returns:
        DataFrame
            A DataFrame containing the aggregated transaction amounts by
            'merchant_id' and 'mcc', sorted in descending order of the total
            transaction amount. Includes a column with MCC descriptions.

        Raises:
            KeyError: If the provided state doesn't exist in the transaction data.
        """
        if state in self._cache_most_valuable_merchant:
            return self._cache_most_valuable_merchant[state]

        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        df_sums = (
            df.groupby(["merchant_id", "mcc"], sort=False)["amount"]
            .sum()
            .reset_index(name="merchant_sum")
            .sort_values("merchant_sum", ascending=False)
        )

        # Pre-compute MCC descriptions for all unique MCCs
        unique_mccs = df_sums['mcc'].unique()
        mcc_desc_map = {mcc: get_mcc_description_by_merchant_id(self.df_mcc, int(mcc)) for mcc in unique_mccs}

        # Use vectorized mapping instead of apply
        df_sums["mcc_desc"] = df_sums["mcc"].map(mcc_desc_map)

        self._cache_most_valuable_merchant[state] = df_sums
        return df_sums

    def get_most_valuable_merchant(self, state: str = None) -> MerchantKPI:
        """
        Fetches the most valuable merchant based on the given state and associated metrics.

        This method determines the top-performing merchant by analyzing transaction data,
        and optionally filters the data by a specific state. It utilizes auxiliary methods
        to calculate the necessary metrics and retrieve MCC (Merchant Category Code)
        descriptions.

        Args:
            state (str, optional): A specific state used to filter merchant transaction
            data. Defaults to None.

        Returns:
            MerchantKPI: An object containing details about the most valuable merchant,
            including its ID, MCC, MCC description, and the total transaction value.
        """
        # Reuse get_merchant_values_by_state to avoid duplicate logic.
        df_sums = self.get_merchant_values_by_state(state)
        top = df_sums.iloc[0]

        return MerchantKPI(
            id=int(top["merchant_id"]),
            mcc=int(top["mcc"]),
            mcc_desc=get_mcc_description_by_merchant_id(self.df_mcc, int(top["mcc"])),
            value=f"{float(top['merchant_sum']):,.2f}"
        )

    def get_transaction_counts_by_hour(self, state: str = None) -> pd.DataFrame:
        """
        Retrieves transaction counts grouped by hour with an optional state filter.

        This method calculates the number of transactions grouped by hour of the day.
        It can filter transactions by a specific state if provided. The results are
        sorted in descending order by transaction count. The computed results are
        also cached for efficiency.

        Parameters:
        state: str, optional
            The name of the state to filter transactions by. If None, transactions
            from all states are considered.

        Returns:
        pd.DataFrame
            A DataFrame containing two columns:
            - 'hour': The hour of the day (0-23).
            - 'transaction_count': The number of transactions that occurred in each
               hour, sorted in descending order.
        """
        # Cache-Check
        if state in self._cache_transaction_counts_by_hour:
            return self._cache_transaction_counts_by_hour[state]

        # Filter state
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Extract hour directly without copying the entire dataframe
        # Convert date to datetime only if it's not already
        if not pd.api.types.is_datetime64_dtype(df["date"]):
            hours = pd.to_datetime(df["date"]).dt.hour
        else:
            hours = df["date"].dt.hour

        # Group & count more efficiently
        df_counts = (
            pd.DataFrame({'hour': hours})
            .groupby("hour", sort=False)
            .size()
            .reset_index(name="transaction_count")
            .sort_values("transaction_count", ascending=False)
        )

        # Cache & return
        self._cache_transaction_counts_by_hour[state] = df_counts
        return df_counts

    def get_peak_hour(self, state: str = None) -> PeakHourKPI:
        """
        Determines the hour with the highest transaction activity and formats the data into
        a PeakHourKPI object. The method calculates the hourly transaction count for a given
        state, identifies the hour with the most activity, formats the hour range and count,
        and returns the information encapsulated in a KPI.

        Args:
        state (str, optional): The specific state to filter the transaction data. Defaults to
        None, indicating no state-based filtering.

        Returns:
        PeakHourKPI: An object representing the hour range with the highest transaction count
        and the formatted count value.
        """
        # Reuse the DataFrame-method
        df_counts = self.get_transaction_counts_by_hour(state)

        # Pick the top row
        top = df_counts.iloc[0]
        most_active_hour = int(top["hour"])
        count = int(top["transaction_count"])

        # Format hour range
        hour_str = f"{most_active_hour:02d}:00 – {(most_active_hour + 1) % 24:02d}:00"
        # Format value with thousands separator
        value_str = f"{count:,}".replace(",", ".")

        # Build and return KPI
        return PeakHourKPI(hour_range=hour_str, value=value_str)

    def get_spending_by_user(self, state: str = None) -> pd.DataFrame:
        """
        Computes the total spending by users filtered by an optional state, caches the result,
        and returns the data as a sorted DataFrame.

        Parameters
        ----------
        state : str, optional
            The name of the state to filter the transactions by. If None, all transaction
            data is considered.

        Returns
        -------
        pd.DataFrame
            A DataFrame with two columns: 'client_id' and 'spending', where 'spending'
            represents the total amount spent by each user. The DataFrame is sorted in
            descending order by 'spending'.
        """
        # Cache-Check
        if state in self._cache_spending_by_user:
            return self._cache_spending_by_user[state]

        # Filter data by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Sum spending per client more efficiently
        df_sums = (
            df.groupby("client_id", sort=False)["amount"]
            .sum()
            .reset_index(name="spending")
            .sort_values("spending", ascending=False)
        )

        # Cache & return
        self._cache_spending_by_user[state] = df_sums
        return df_sums

    def get_top_spending_user(self, state: str = None) -> UserKPI:
        """
        Determines the top spending user for a given state or overall based on the
        highest spending. Retrieves additional user details to construct the result.

        Arguments:
        state: str or None
            Optional. Specifies the U.S. state for filtering. If None, considers all
            states.

        Returns:
        UserKPI
            An object containing details of the top spending user, including their
            ID, gender, current age, and the formatted spending value.
        """
        # Reuse DataFrame-method
        df_sums = self.get_spending_by_user(state)
        top = df_sums.iloc[0]
        client_id = int(top["client_id"])
        spending = float(top["spending"])

        # Lookup additional user details
        user_row = self.df_users.loc[self.df_users["id"] == client_id].iloc[0]
        gender = user_row["gender"]
        current_age = int(user_row["current_age"])

        # Format spending value
        value_str = f"{spending:,.2f}"

        return UserKPI(
            id=client_id,
            gender=gender,
            current_age=current_age,
            value=value_str
        )

    def get_visits_by_merchant(self, state: str = None) -> pd.DataFrame:
        """
        Retrieves the number of visits to merchants based on transaction data. Optionally filters
        the result by a specific state.

        Args:
            state (str, optional): The name of the state to filter transaction data by. If not
            provided, visits are calculated for all data. Default is None.

        Returns:
            pd.DataFrame: A DataFrame containing the number of visits to each merchant, along
            with the merchant category code (MCC) and its description.

        Raises:
            None
        """
        if state in self._cache_visits_by_merchant:
            return self._cache_visits_by_merchant[state]

        # Filter by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Create a mapping of merchant_id to mcc once
        merchant_mcc_map = df[['merchant_id', 'mcc']].drop_duplicates('merchant_id').set_index('merchant_id')[
            'mcc'].to_dict()

        # Pre-compute MCC descriptions for all unique MCCs
        unique_mccs = set(merchant_mcc_map.values())
        mcc_desc_map = {mcc: get_mcc_description_by_merchant_id(self.df_mcc, mcc) for mcc in unique_mccs}

        # Aggregate visits by merchant more efficiently
        visit_counts = (
            df.groupby("merchant_id", sort=False)
            .size()
            .reset_index(name="visits")
            .sort_values("visits", ascending=False)
        )

        # Use vectorized operations instead of apply
        visit_counts['mcc'] = visit_counts['merchant_id'].map(merchant_mcc_map)
        visit_counts['mcc_desc'] = visit_counts['mcc'].map(mcc_desc_map)

        self._cache_visits_by_merchant[state] = visit_counts
        return visit_counts

    def get_most_visited_merchant(self, state: str = None) -> VisitKPI:
        """
        Retrieves the most visited merchant data based on visit count. The merchant with the highest number of visits in the
        specified state is determined. The result includes merchant ID, MCC, MCC description, and formatted visit count.

        Args:
            state (str, optional): The state for which the most visited merchant should be retrieved. If not provided, the search
                                   will not be state-specific.

        Returns:
            VisitKPI: An object containing the most visited merchant's data including merchant ID, MCC, MCC description, and
                      formatted visit count.
        """
        df_visits = self.get_visits_by_merchant(state)
        top = df_visits.iloc[0]
        mid = int(top["merchant_id"])
        visits = int(top["visits"])
        mcc = int(top["mcc"])
        desc = top["mcc_desc"]

        visits_str = f"{visits:,}".replace(",", ".")
        return VisitKPI(id=mid, mcc=mcc, mcc_desc=desc, visits=visits_str)

    def _calc_home_tab_kpis(self):
        """
        Calculates the Key Performance Indicators (KPIs) required for the Home Tab. This function logs
        the start of the KPI calculation and uses benchmark tracking to log the time taken for the
        calculation process. It performs several operations to fetch specific KPI values related to
        merchants and users.
        """
        logger.log("ℹ️ Home: Calculating KPIs for Home Tab...", 3)
        bm = Benchmark("Home: Calculating KPIs for Home Tab")
        self.get_most_valuable_merchant()
        self.get_most_visited_merchant()
        self.get_top_spending_user()
        self.get_peak_hour()
        bm.print_time(level=4)

    def get_expenditures_by_gender(self, state: str = None) -> dict[str, float]:
        """
        Calculates the total expenditures grouped by gender, with an optional filter for a specific state. The function
        utilizes a caching mechanism to optimize repeated queries for the same state.

        Arguments:
        state: str, optional
            The name of the state to filter the transactions. If not provided, the calculation is performed
            on all available data.

        Returns:
        dict[str, float]
            A dictionary where keys are gender identifiers and the values are the total expenditures associated
            with each gender.

        """
        # Cache-Check
        if state in self._cache_expenditures_by_gender:
            return self._cache_expenditures_by_gender[state]

        # Optional filter without copying
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Merge with user gender more efficiently
        df_merged = pd.merge(
            df[["client_id", "amount"]],
            self.df_users[["id", "gender"]],
            left_on="client_id",
            right_on="id",
            how="left",
            sort=False  # Avoid unnecessary sorting
        )

        # Group & sum more efficiently
        gender_sums = (
            df_merged
            .groupby("gender", sort=False)["amount"]
            .sum()
            .to_dict()
        )

        # Keys uppercased - do this more efficiently
        gender_sums = {(str(k).upper() if pd.notna(k) else "UNKNOWN"): v for k, v in gender_sums.items()}

        # Cache & return
        self._cache_expenditures_by_gender[state] = gender_sums
        return gender_sums

    def get_expenditures_by_age(self, state: str = None) -> dict[str, float]:
        """
        Calculates the total expenditures per age group, optionally filtering by state.

        This function processes transaction data by merging it with user age data, creating
        age groups (e.g., "20-30", "30-40", etc.), and then summing transaction amounts
        within each age group. It can also filter the transactions by a specified state.

        Parameters:
            state (str, optional): The name of the state to filter transactions by. Defaults to None.

        Returns:
            dict[str, float]: A dictionary where keys represent age groups, and values represent
            the corresponding total expenditures.

        """
        # Cache-Check
        if state in self._cache_expenditures_by_age:
            return self._cache_expenditures_by_age[state]

        # Optional filter without copying
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Merge with user ages more efficiently
        df_merged = pd.merge(
            df[["client_id", "amount"]],
            self.df_users[["id", "current_age"]],
            left_on="client_id",
            right_on="id",
            how="left",
            sort=False  # Avoid unnecessary sorting
        )

        # Create age groups more efficiently
        # First calculate the decade (floor division by 10)
        decades = df_merged["current_age"].floordiv(10)
        # Create age groups directly
        df_merged["age_group"] = (decades * 10).astype(str) + "-" + ((decades * 10) + 10).astype(str)

        # Group by age group and sum amounts more efficiently
        age_group_sums = (
            df_merged
            .groupby("age_group", sort=False)["amount"]
            .sum()
            .to_dict()
        )

        # Cache & return
        self._cache_expenditures_by_age[state] = age_group_sums
        return age_group_sums

    def get_expenditures_by_channel(self, state: str = None) -> dict[str, float]:
        """
        Calculates the total expenditures divided by transaction channels,
        optionally filtered by a given U.S. state. Results are cached per state.

        Parameters
        ----------
        state : str, optional
            If provided, only 'Swipe Transaction' in this state are considered
            for the In-Store sum. Online transactions are always global.

        Returns
        -------
        dict[str, float]
            A dictionary where keys are the transaction channels
            ("Online" or "In-Store"), and values represent the summed expenditures
            for each channel.
        """
        # Cache-Check
        if state in self._cache_expenditures_by_channel:
            return self._cache_expenditures_by_channel[state]

        # Work without copying
        df = self.df_transactions

        # Normalize and check use_chip more efficiently
        # Avoid creating a new column by using Series operations directly
        use_chip_lower = df["use_chip"].str.strip().str.lower()

        # All online transactions (state_name may be null)
        online_mask = use_chip_lower.str.startswith("online")
        online_sum = df.loc[online_mask, "amount"].sum()

        # In-Store: only swipe transactions, optionally filtered by state
        if state == "ONLINE":
            instore_sum = 0  # No In-store for Online Transactions
        else:
            instore_mask = use_chip_lower.str.startswith("swipe")
            if state:
                instore_mask &= (df["state_name"] == state)
            instore_sum = df.loc[instore_mask, "amount"].sum()

        result = {
            "ONLINE": online_sum,
            "IN-STORE": instore_sum
        }

        # Cache & return
        self._cache_expenditures_by_channel[state] = result
        return result

    def _cache_map_data(self) -> None:
        """
        Caches the USA map data for the home tab by loading it from a cache or computing it from
        the provided transaction DataFrame. The function optimizes data processing to reduce memory
        usage and computational overhead.

        Pre-caching involves either directly retrieving data from a previously saved cache file or
        performing a series of filtering, grouping, and transformation operations on the transaction
        DataFrame to generate the required map data. The function incorporates various utility
        methods to load and save cached data and measures performance using benchmarking tools.

        Raises:
            None
        """
        logger.log("🔄 Home: Pre-caching USA Map data...", indent_level=3)
        bm_cache_map = Benchmark("Home: Pre-caching USA Map data")

        # Try to load map data from cache first
        map_data = self.data_manager.load_cache_from_disk("home_tab_map_data")
        if map_data is not None:
            self.map_data = map_data
            logger.log("✅ Home: Loaded map data from cache", indent_level=4)
            bm_cache_map.print_time(level=4)
            return

        # More efficient approach without copying the entire dataframe
        df = self.df_transactions

        # Filter out rows with null state_name
        df_filtered = df.dropna(subset=["state_name"])

        # Group and count more efficiently
        state_counts = (
            df_filtered
            .groupby("state_name", sort=False, as_index=False)
            .size()
            .rename(columns={"size": "transaction_count"})
        )

        # Add uppercase state names for easier matching
        state_counts["state_name_upper"] = state_counts["state_name"].str.upper()

        self.map_data = state_counts

        # Save map data to cache
        self.data_manager.save_cache_to_disk("home_tab_map_data", self.map_data)

        bm_cache_map.print_time(level=4)

    def _save_caches_to_disk(self):
        """
        Save all cached data to disk.
        """
        logger.log("🔄 Home: Saving caches to disk...", indent_level=3)
        bm = Benchmark("Home: Saving caches to disk")

        # Save all cache dictionaries
        cache_data = {
            "most_valuable_merchant": self._cache_most_valuable_merchant,
            "visits_by_merchant": self._cache_visits_by_merchant,
            "spending_by_user": self._cache_spending_by_user,
            "transaction_counts_by_hour": self._cache_transaction_counts_by_hour,
            "expenditures_by_gender": self._cache_expenditures_by_gender,
            "expenditures_by_age": self._cache_expenditures_by_age,
            "expenditures_by_channel": self._cache_expenditures_by_channel
        }

        self.data_manager.save_cache_to_disk("home_tab_caches", cache_data)

        # Save map data separately as it's a DataFrame
        if not self.map_data.empty:
            self.data_manager.save_cache_to_disk("home_tab_map_data", self.map_data)

        bm.print_time(level=4)

    def _load_caches_from_disk(self) -> bool:
        """
        Load all cached data from disk.

        Returns:
            bool: True if caches were successfully loaded, False otherwise
        """
        logger.log("🔄 Home: Loading caches from disk...", indent_level=3)
        bm = Benchmark("Home: Loading caches from disk")

        # Load cache dictionaries
        cache_data = self.data_manager.load_cache_from_disk("home_tab_caches", is_dataframe=False)
        if cache_data is not None:
            self._cache_most_valuable_merchant = cache_data.get("most_valuable_merchant", {})
            self._cache_visits_by_merchant = cache_data.get("visits_by_merchant", {})
            self._cache_spending_by_user = cache_data.get("spending_by_user", {})
            self._cache_transaction_counts_by_hour = cache_data.get("transaction_counts_by_hour", {})
            self._cache_expenditures_by_gender = cache_data.get("expenditures_by_gender", {})
            self._cache_expenditures_by_age = cache_data.get("expenditures_by_age", {})
            self._cache_expenditures_by_channel = cache_data.get("expenditures_by_channel", {})

            # Load map data
            map_data = self.data_manager.load_cache_from_disk("home_tab_map_data")
            if map_data is not None:
                self.map_data = map_data

            bm.print_time(level=4)
            return True

        bm.print_time(level=4)
        return False

    def _pre_cache_home_tab_data(self) -> None:
        """
        Pre-caches data for the Home-Tab view by performing data aggregation and calculations for
        both overall data and state-specific data. This method is intended to optimize subsequent
        data retrieval and ensure that necessary insights are readily available for analysis. The
        method executes a series of predefined data aggregation functions for all states in the
        transaction dataset.

        Raises
        ------
        None

        Returns
        -------
        None
        """
        import concurrent.futures
        import multiprocessing

        logger.log("🔄 Home: Pre-caching Home-Tab States data...", indent_level=3)
        bm_pre_cache_full = Benchmark("Home: Pre-caching Home-Tab States data")

        # Try to load caches from disk first
        if self._load_caches_from_disk():
            logger.log("✅ Home: Successfully loaded caches from disk", indent_level=3)
            bm_pre_cache_full.print_time(level=4)
            return

        # Caching functions to run for each state
        caching_functions: list[Callable[[str | None], Any]] = [
            self.get_merchant_values_by_state,
            self.get_transaction_counts_by_hour,
            self.get_spending_by_user,
            self.get_visits_by_merchant,
            self.get_expenditures_by_gender,
            self.get_expenditures_by_age,
            self.get_expenditures_by_channel
        ]

        # First for overall (state=None) - this is often a dependency for state-specific data
        bm_usa_wide = Benchmark("Home: Pre-caching of USA-wide data")
        for func in caching_functions:
            func(None)
        bm_usa_wide.print_time(level=4)

        # Get all states
        states = self.df_transactions['state_name'].dropna().unique().tolist()

        # Skip if no states to process
        if not states:
            logger.log("ℹ️ Home: No states to process", indent_level=3)
            bm_pre_cache_full.print_time(level=4)
            return

        # Determine optimal batch size based on number of states and CPU cores
        # This helps reduce thread creation overhead while still utilizing parallelism
        num_cores = multiprocessing.cpu_count()
        batch_size = max(1, min(10, len(states) // num_cores))

        # Create batches of states
        state_batches = [states[i:i + batch_size] for i in range(0, len(states), batch_size)]

        # Define a function to cache data for a batch of states
        def cache_state_batch(state_batch):
            results = []
            for state in state_batch:
                # Process each function for this state
                for func in caching_functions:
                    func(state)
                results.append(state)
            return results

        # Use ThreadPoolExecutor for parallel processing of state batches
        bm_states = Benchmark("Home: Pre-caching data for all states in batches")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
            # Process batches of states in parallel
            all_results = []
            futures = [executor.submit(cache_state_batch, batch) for batch in state_batches]

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())

        bm_states.print_time(level=4)

        # Save caches to disk for future use
        self._save_caches_to_disk()

        bm_pre_cache_full.print_time(level=4)

    def initialize(self):
        """
        Initializes the necessary processes for setting up internal data structures
        and preloading cache configurations. It organizes tasks for transaction
        data processing, key performance indicators calculation, and caching
        necessary data for efficient system operation.

        """
        logger.log("ℹ️ Home: Initializing Home Tab Data...", 3, add_line_before=True)
        bm = Benchmark("Home: Initialization")

        self._calc_home_tab_kpis()
        self._pre_cache_home_tab_data()
        self._cache_map_data()

        bm.print_time(level=4, add_empty_line=True)
