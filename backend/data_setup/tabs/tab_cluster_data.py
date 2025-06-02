from typing import List

import pandas as pd
from sklearn.cluster import KMeans

from utils import logger
from utils.benchmark import Benchmark


class ClusterTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users

        # Initialize dataframes and data
        self.mcc = None
        self.data_file = None

        # Age group bins and labels
        self.age_bins = [0, 25, 35, 45, 55, 65, 200]
        self.age_labels = ['<25', '26–35', '36–45', '46–55', '56–65', '65+']

        # Caches
        self._cache_cluster_data = {}
        self._cache_inc_vs_exp_cluster_data = {}

    def get_cluster_merchant_group_dropdown(self) -> List[str]:
        """
        Generate a sorted list of unique merchant groups for a dropdown menu.

        Returns:
            list: Sorted list of merchant groups with 'All Merchant Groups' as the first option.
        """
        my_list = sorted(self.mcc['merchant_group'].unique().tolist())
        my_list.insert(0, 'All Merchant Groups')
        return my_list

    def prepare_cluster_data(self, merchant_group) -> pd.DataFrame:
        """
        Prepare and cluster transaction data based on transaction count and value.

        Args:
            merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

        Returns:
            pd.DataFrame: Aggregated data with cluster labels based on total and average transaction values.
        """
        # Check cache
        cache_key = f"cluster_data_{merchant_group}"
        if cache_key in self._cache_cluster_data:
            return self._cache_cluster_data[cache_key]

        # Use view
        if merchant_group != 'All Merchant Groups':
            df_view = self.data_file[self.data_file['merchant_group'] == merchant_group]
        else:
            df_view = self.data_file

        # Aggregation per client_id
        agg = df_view.groupby('client_id').agg(
            transaction_count=('amount', 'count'),
            total_value=('amount', 'sum'),
            age_group=('age_group', 'first')  # one age group per client
        ).reset_index()

        agg['average_value'] = agg['total_value'] / agg['transaction_count']

        # Check the number of data points
        n_samples = len(agg)

        # Clustering 1: total_value vs count
        n_clusters_total = min(4, n_samples)
        if n_clusters_total >= 1:
            kmeans_total = KMeans(n_clusters=n_clusters_total, random_state=42, n_init=10)
            cluster_data = agg[['transaction_count', 'total_value']]
            agg['cluster_total'] = kmeans_total.fit_predict(cluster_data)
        else:
            agg['cluster_total'] = 0  # fallback for 0 rows
        agg['cluster_total_str'] = agg['cluster_total'].astype(str)

        # Clustering 2: average_value vs count
        n_clusters_avg = min(4, n_samples)
        if n_clusters_avg >= 1:
            kmeans_avg = KMeans(n_clusters=n_clusters_avg, random_state=42, n_init=10)
            cluster_data = agg[['transaction_count', 'average_value']]
            agg['cluster_avg'] = kmeans_avg.fit_predict(cluster_data)
        else:
            agg['cluster_avg'] = 0
        agg['cluster_avg_str'] = agg['cluster_avg'].astype(str)

        # Cache the result
        self._cache_cluster_data[cache_key] = agg

        return agg

    def prepare_inc_vs_exp_cluster_data(self, merchant_group) -> pd.DataFrame:
        """
        Prepare and cluster data based on yearly income versus total expenses.

        Args:
            merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

        Returns:
            pd.DataFrame: Aggregated data with clusters for income vs expenses.
        """
        # Check cache
        cache_key = f"inc_vs_exp_cluster_data_{merchant_group}"
        if cache_key in self._cache_inc_vs_exp_cluster_data:
            return self._cache_inc_vs_exp_cluster_data[cache_key]

        # Use view instead of copy when possible
        if merchant_group != 'All Merchant Groups':
            # Filter data without creating an unnecessary copy
            df_view = self.data_file[self.data_file['merchant_group'] == merchant_group]
        else:
            df_view = self.data_file

        # Aggregation per client_id - more efficient with named aggregation
        agg = df_view.groupby('client_id').agg(
            total_expenses=('amount', 'sum'),
            yearly_income=('yearly_income', 'first'),
            age_group=('age_group', 'first')
        ).reset_index()

        # drop NaNs
        agg = agg.dropna(subset=['total_expenses', 'yearly_income'])

        n_samples = len(agg)
        n_clusters = min(4, n_samples)

        if n_clusters >= 1:
            # Reduced n_init for better performance while maintaining reproducibility
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            # Extract only needed columns for clustering to reduce memory usage
            cluster_data = agg[['yearly_income', 'total_expenses']]
            agg['cluster_inc_vs_exp'] = kmeans.fit_predict(cluster_data)
        else:
            agg['cluster_inc_vs_exp'] = 0

        agg['cluster_inc_vs_exp_str'] = agg['cluster_inc_vs_exp'].astype(str)

        # Cache the result
        self._cache_inc_vs_exp_cluster_data[cache_key] = agg

        return agg

    def get_data_file(self) -> pd.DataFrame:
        """
        Get the processed data file with age groups.

        Returns:
            pd.DataFrame: The processed data file.
        """
        return self.data_file

    def _save_caches_to_disk(self):
        """
        Saves cluster-related cache data to disk.

        This method consolidates and saves multiple cache dictionaries to disk to preserve
        their state. It utilizes a benchmarking utility to measure the time required for
        this save operation and provides a log entry for tracking purposes. Persisting
        cache data is crucial for ensuring that cluster-related computations can resume
        without redundant processing.

        Raises:
            Any exception or error arising from data storage operations will be logged or
            handled internally.

        Attributes:
            _cache_cluster_data: dict
                A cache dictionary containing general cluster data.
            _cache_inc_vs_exp_cluster_data: dict
                A cache dictionary containing incremental versus expansion cluster data.

        """
        logger.log("🔄 Cluster: Saving caches to disk...", indent_level=3)
        bm = Benchmark("Cluster: Saving caches to disk")

        # Save all cache dictionaries
        cache_data = {
            "cluster_data": self._cache_cluster_data,
            "inc_vs_exp_cluster_data": self._cache_inc_vs_exp_cluster_data
        }

        self.data_manager.save_cache_to_disk("cluster_tab_caches", cache_data)
        bm.print_time(level=4)

    def _load_caches_from_disk(self) -> bool:
        """
        Load all cached data from disk.

        Returns:
            bool: True if caches were successfully loaded, False otherwise
        """
        logger.log("🔄 Cluster: Loading caches from disk...", indent_level=3)
        bm = Benchmark("Cluster: Loading caches from disk")

        # Load cache dictionaries
        cache_data = self.data_manager.load_cache_from_disk("cluster_tab_caches", is_dataframe=False)
        if cache_data is not None:
            self._cache_cluster_data = cache_data.get("cluster_data", {})
            self._cache_inc_vs_exp_cluster_data = cache_data.get("inc_vs_exp_cluster_data", {})
            bm.print_time(level=4)
            return True

        bm.print_time(level=4)
        return False

    def _pre_cache_cluster_tab_data(self) -> None:
        """
        Caches data for the Cluster Tab by preloading necessary information.

        This method is responsible for pre-caching the data required for the Cluster Tab in
        the application. It attempts to load data from disk first and, if unavailable, proceeds to
        generate and cache the data for both "All Merchant Groups" and individual merchant
        groups using concurrent processing for efficiency. This caching improves overall
        application performance and responsiveness during runtime.

        The method utilizes benchmarks for tracking the performance of each step and logs
        the progress accordingly. If the data is successfully loaded from disk, it will skip
        the computationally intensive tasks and directly return.

        Attributes:
            None

        Args:
            None

        Returns:
            None
        """
        import concurrent.futures

        logger.log("🔄 Cluster: Pre-caching Cluster Tab data...", indent_level=3)
        bm_pre_cache_full = Benchmark("Cluster: Pre-caching Cluster Tab data")

        # Try to load caches from disk first
        if self._load_caches_from_disk():
            logger.log("✅ Cluster: Successfully loaded caches from disk", indent_level=3)
            bm_pre_cache_full.print_time(level=4)
            return

        # Cache data for 'All Merchant Groups' first as it's often a dependency
        bm_all_groups = Benchmark("Cluster: Pre-caching data for All Merchant Groups")
        self.prepare_cluster_data('All Merchant Groups')
        self.prepare_inc_vs_exp_cluster_data('All Merchant Groups')
        bm_all_groups.print_time(level=4)

        # Define a function to cache data for a merchant group
        def cache_merchant_group_data(group):
            # Cache both types of cluster data for this merchant group
            self.prepare_cluster_data(group)
            self.prepare_inc_vs_exp_cluster_data(group)
            return group

        # Get merchant groups (skip 'All Merchant Groups' as it's already cached)
        merchant_groups = self.get_cluster_merchant_group_dropdown()[1:]

        # Use ThreadPoolExecutor for parallel processing
        # This is ideal for CPU-bound operations like clustering
        # The max_workers parameter can be adjusted based on the system's capabilities
        bm_groups = Benchmark("Cluster: Pre-caching data for all merchant groups in parallel")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Process all merchant groups in parallel
            results = list(executor.map(cache_merchant_group_data, merchant_groups))

        bm_groups.print_time(level=4)

        # Save caches to disk for future use
        self._save_caches_to_disk()

        bm_pre_cache_full.print_time(level=4)

    def initialize(self):
        """
        Initialize the cluster tab data by loading and processing the necessary data.
        """
        logger.log("ℹ️ Cluster: Initializing Cluster Tab Data...", 3, add_line_before=True)
        bm = Benchmark("Cluster: Initialization")

        # Use shared MCC codes from data manager
        self.mcc = self.data_manager.df_mcc

        # Use shared transactions_mcc_users from data manager
        # This avoids duplicate processing and improves performance
        self.data_file = self.data_manager.transactions_mcc_users.copy()

        # Add age_group
        self.data_file['age_group'] = pd.cut(
            self.data_file['current_age'],
            bins=self.age_bins,
            labels=self.age_labels
        )

        # Pre-cache cluster data
        self._pre_cache_cluster_tab_data()

        bm.print_time(level=4, add_empty_line=True)
