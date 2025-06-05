"""
Module for centralized data caching in the application.

This module provides functionality to check if all necessary caches exist,
load data from caches if they do, and create caches if they don't.
"""

import os

import utils.logger as logger
from backend.data_setup.tabs.tab_cluster_data import ClusterTabData
from backend.data_setup.tabs.tab_home_data import HomeTabData
from backend.data_setup.tabs.tab_merchant_data import MerchantTabData
from backend.data_setup.tabs.tab_user_data import UserTabData
from utils.benchmark import Benchmark


class DataCacher:
    """
    Handles centralized data caching for the application.

    This class provides methods to check if all necessary caches exist,
    load data from caches if they do, and create caches if they don't.
    """

    def __init__(self, data_manager):
        """
        Initialize the DataCacher with a reference to the DataManager.

        Args:
            data_manager: The DataManager instance to use for caching operations.
        """
        self.data_manager = data_manager
        self.cache_dir = data_manager.cache_dir

    def cache_exists(self) -> bool:
        """
        Check if all necessary caches exist.

        Returns:
            bool: True if all necessary caches exist, False otherwise.
        """
        # Check if cache directory exists
        if not self.cache_dir.exists():
            return False

        # List of essential cache files that must exist
        essential_caches = [
            "transactions_mcc.parquet",
            "transactions_mcc_users.parquet",
            "home_tab_caches.pkl",
            "home_tab_map_data.parquet",
            "merchant_tab_caches.pkl",
            "cluster_tab_caches.pkl",
            "user_transactions_df.parquet",
            "user_merchant_agg_df.parquet",
            "cards_data_processed.parquet",
            "users_data_processed.parquet",
            "transactions_data_processed.parquet"
        ]

        # Check if all essential cache files exist
        for cache_file in essential_caches:
            if not (self.cache_dir / cache_file).exists():
                logger.log(f"ℹ️ Cache file missing: {cache_file}", indent_level=2)
                return False

        logger.log("✅ All cache files exist", indent_level=2)
        return True

    def load_from_cache(self) -> bool:
        """
        Load all data from cache.

        This method assumes that the basic data frames (df_users, df_transactions, df_cards, df_mcc)
        have already been loaded by the DataManager.

        Returns:
            bool: True if all data was successfully loaded from cache, False otherwise.
        """
        logger.log("ℹ️ Loading data from cache...", indent_level=3)
        bm = Benchmark("Loading data from cache")

        try:
            # Load shared data
            self.data_manager.transactions_mcc = self.data_manager.load_cache_from_disk("transactions_mcc")
            self.data_manager.transactions_mcc_users = self.data_manager.load_cache_from_disk("transactions_mcc_users")

            if self.data_manager.transactions_mcc is None or self.data_manager.transactions_mcc_users is None:
                logger.log("⚠️ Failed to load shared data from cache", indent_level=2)
                return False

            # Create tab data instances
            from backend.data_setup.tabs.tab_home_data import HomeTabData
            from backend.data_setup.tabs.tab_merchant_data import MerchantTabData
            from backend.data_setup.tabs.tab_cluster_data import ClusterTabData
            from backend.data_setup.tabs.tab_user_data import UserTabData

            self.data_manager.home_tab_data = HomeTabData(self.data_manager)
            self.data_manager.merchant_tab_data = MerchantTabData(self.data_manager)
            self.data_manager.cluster_tab_data = ClusterTabData(self.data_manager)
            self.data_manager.user_tab_data = UserTabData(self.data_manager)

            # Initialize tab data in parallel (this will load from cache)
            import concurrent.futures
            logger.log("🔄 DataCacher: Initializing tab data in parallel...", indent_level=2)
            bm_parallel_init = Benchmark("DataCacher: Parallel tab data initialization from cache")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit all initialization tasks in parallel
                future_home = executor.submit(self.data_manager.home_tab_data.initialize)
                future_merchant = executor.submit(self.data_manager.merchant_tab_data.initialize)
                future_cluster = executor.submit(self.data_manager.cluster_tab_data.initialize)
                future_user = executor.submit(self.data_manager.user_tab_data.initialize)

                # Wait for all tasks to complete
                concurrent.futures.wait([future_home, future_merchant, future_cluster, future_user])

            bm_parallel_init.print_time(level=2)

            # Calculate basic metrics
            self.data_manager.amount_of_transactions = len(self.data_manager.df_transactions)
            self.data_manager.sum_of_transactions = self.data_manager.df_transactions["amount"].sum()
            self.data_manager.avg_transaction_amount = self.data_manager.sum_of_transactions / self.data_manager.amount_of_transactions

            bm.print_time(level=1)
            return True
        except Exception as e:
            logger.log(f"⚠️ Error loading from cache: {str(e)}", indent_level=2)
            bm.print_time(level=1)
            return False

    def create_cache(self) -> bool:
        """
        Create all necessary caches by running the data processing.

        This method assumes that the basic data frames (df_users, df_transactions, df_cards, df_mcc)
        have already been loaded by the DataManager.

        Returns:
            bool: True if cache was successfully created, False otherwise.
        """
        logger.log("ℹ️ Creating cache...", indent_level=1)
        bm = Benchmark("Creating cache")

        try:
            # Create cache directory if it doesn't exist
            if not self.cache_dir.exists():
                os.makedirs(self.cache_dir, exist_ok=True)
                logger.log(f"ℹ️ Created cache directory: {self.cache_dir}", indent_level=2)

            # Prepare shared data that will be used by multiple tabs
            # This will also save the shared data to cache
            self.data_manager.prepare_shared_data()

            # Create tab data instances
            self.data_manager.home_tab_data = HomeTabData(self.data_manager)
            self.data_manager.merchant_tab_data = MerchantTabData(self.data_manager)
            self.data_manager.cluster_tab_data = ClusterTabData(self.data_manager)
            self.data_manager.user_tab_data = UserTabData(self.data_manager)

            # Initialize tab data in parallel
            import concurrent.futures
            logger.log("🔄 DataCacher: Initializing tab data in parallel...", indent_level=2)
            bm_parallel_init = Benchmark("DataCacher: Parallel tab data initialization")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit all initialization tasks in parallel
                future_home = executor.submit(self.data_manager.home_tab_data.initialize)
                future_merchant = executor.submit(self.data_manager.merchant_tab_data.initialize)
                future_cluster = executor.submit(self.data_manager.cluster_tab_data.initialize)
                future_user = executor.submit(self.data_manager.user_tab_data.initialize)

                # Wait for all tasks to complete
                concurrent.futures.wait([future_home, future_merchant, future_cluster, future_user])

            bm_parallel_init.print_time(level=2)

            # Calculate basic metrics
            self.data_manager.amount_of_transactions = len(self.data_manager.df_transactions)
            self.data_manager.sum_of_transactions = self.data_manager.df_transactions["amount"].sum()
            self.data_manager.avg_transaction_amount = self.data_manager.sum_of_transactions / self.data_manager.amount_of_transactions

            logger.log("✅ Cache created successfully", indent_level=2)
            bm.print_time(level=1)
            return True
        except Exception as e:
            logger.log(f"⚠️ Error creating cache: {str(e)}", indent_level=2)
            bm.print_time(level=1)
            return False
