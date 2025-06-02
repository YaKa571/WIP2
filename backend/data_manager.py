import os
import pickle
from pathlib import Path
from typing import Optional

import pandas as pd
import pgeocode
import us

import utils.logger as logger
from backend.data_cacher import DataCacher
from backend.data_handler import optimize_data, clean_units, json_to_df, \
    read_parquet_data, set_minor_merchants_threshold
from backend.data_setup.tabs.tab_cluster_data import ClusterTabData
from backend.data_setup.tabs.tab_home_data import HomeTabData
from backend.data_setup.tabs.tab_merchant_data import MerchantTabData
from backend.data_setup.tabs.tab_user_data import UserTabData
from components.constants import DATA_DIRECTORY, CACHE_DIRECTORY
from utils.benchmark import Benchmark
from utils.utils import rounded_rect


class DataManager:
    """
    Manages data initialization, preprocessing, and storage for use in a larger application.

    The DataManager class is designed as a singleton to ensure a single consistent
    instance throughout its usage. It initializes data-related components, handles
    preprocessing tasks such as processing ZIP codes and state names in transaction data,
    and computes summaries of loaded datasets. Data is read from CSV files, converted to
    parquet files for optimization, cleaned, and updated in memory. Additionally, the class
    provides detailed data summaries and logs progress during its operation.

    Methods:
        initialize: Creates a singleton instance of the class with a specified data
        directory.

        get_instance: Returns the singleton instance of the class.

        process_transaction_zips: Preprocesses and standardizes ZIP codes in the
        transactions dataset.

        process_transaction_states: Maps state abbreviations to their full names in
        the transactions dataset.

        start: Performs the overall data setup and processing operations.
    """

    _instance = None

    @staticmethod
    def initialize(data_dir: Path = DATA_DIRECTORY, num_rows=50_001):  # <-- Change num_rows value here to trigger cache
        if DataManager._instance is None:
            DataManager._instance = DataManager(data_dir, num_rows=num_rows)

    @staticmethod
    def get_instance():
        if DataManager._instance is None:
            raise Exception("⚠️ DataManager has not been initialized. Call DataManager.initialize() first.")
        return DataManager._instance

    def __init__(self, data_dir: Path = DATA_DIRECTORY, num_rows=50_000):
        if DataManager._instance is not None:
            raise Exception("⚠️ Use DataManager.get_instance() instead of creating a new instance.")

        benchmark_data_manager = Benchmark("DataManager initialization")
        logger.log("ℹ️ Initializing DataManager...", indent_level=1)

        self.data_dir = data_dir
        self.cache_dir = data_dir / "cache"
        self._cached_num_rows = None

        # Create cache directory if it doesn't exist
        if not self.cache_dir.exists():
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.log(f"ℹ️ Created cache directory: {self.cache_dir}", indent_level=2)

        # Initialize data cacher
        self.data_cacher = DataCacher(self)

        self.df_users: pd.DataFrame = pd.DataFrame()
        self.df_transactions: pd.DataFrame = pd.DataFrame()
        self.df_cards: pd.DataFrame = pd.DataFrame()
        self.df_mcc: pd.DataFrame = json_to_df("mcc_codes.json", col_names=["mcc", "merchant_group"])
        self.df_train_fraud: pd.DataFrame = pd.DataFrame()
        self.transactions_mcc: pd.DataFrame = pd.DataFrame()
        self.transactions_mcc_users: pd.DataFrame = pd.DataFrame()

        self.amount_of_transactions: int = 0
        self.sum_of_transactions: float = 0.00
        self.avg_transaction_amount: float = 0.00

        self.nomi = pgeocode.Nominatim("us")

        # Home Tab
        self.home_tab_data: Optional[HomeTabData] = None

        # Merchant Tab
        self.merchant_tab_data: Optional[MerchantTabData] = None

        # Cluster Tab
        self.cluster_tab_data: Optional[ClusterTabData] = None

        # User Tab
        self.user_tab_data: Optional[UserTabData] = None

        # Map
        self.online_shape = list[list]

        # Initializing all data
        self.start(num_rows=num_rows)
        benchmark_data_manager.print_time()

    def load_data_frames(self, num_rows=None):
        """
        Loads and processes user, transaction, and card data by utilizing optimized and clean data workflows.
        If cached processed versions of the data exist in the specified cache directory, those are loaded;
        otherwise, the raw data is processed and saved to cache for future use.

        The method ensures that any unnecessary intermediate files are removed, processes transaction-specific
        details, and prepares the data for further analysis.

        Args:
            num_rows (int, optional): Number of rows to load and cache when no cache exists.
                When cache exists, the entire cache is loaded. Defaults to None (load all rows).

        Raises:
            FileNotFoundError: Raised if expected input data files are not found during processing.

        Attributes:
            cache_dir (Path): The directory where cache files are stored.
            df_users (pd.DataFrame): DataFrame containing processed user data.
            df_transactions (pd.DataFrame): DataFrame containing processed transaction data.
            df_cards (pd.DataFrame): DataFrame containing processed card data.
            df_mcc (pd.DataFrame): DataFrame containing merchant category codes (MCC).
        """
        logger.log("ℹ️ DataManager: Loading from files...", 2, add_line_before=True)
        bm = Benchmark("DataManager: Loading from files")

        # Check if num_rows has changed
        cached_num_rows = self._load_num_rows_from_cache()
        if cached_num_rows is not None and num_rows is not None and cached_num_rows != num_rows:
            logger.log(
                f"⚠️ DataManager: num_rows has changed from {cached_num_rows:,} to {num_rows:,}, deleting cache...",
                3)
            self._delete_cache_directory()
            # Reinitialize data cacher after deleting cache
            self.data_cacher = DataCacher(self)
            # Save the new num_rows value
            self._save_num_rows_to_cache(num_rows)
        elif cached_num_rows is None and num_rows is not None:
            # First time setting num_rows
            logger.log(f"ℹ️ DataManager: Setting initial num_rows value to {num_rows}", 2)
            self._save_num_rows_to_cache(num_rows)

        # =============================================== USERS ===============================================

        # Check if users_data_processed.parquet exists in data/cache directory and load it if it does
        # if not run optimize data and clean units
        users_processed_path = self.cache_dir / "users_data_processed.parquet"
        users_to_del_path = self.cache_dir / "users_data.parquet"

        if users_processed_path.exists():
            logger.log(f"ℹ️ Loading processed users data from cache: {users_processed_path}", 3)
            self.df_users = pd.read_parquet(users_processed_path)

            if users_to_del_path.exists():
                os.remove(users_to_del_path)
                logger.log(f"🗑️ Deleted: {users_to_del_path}", 3)

        else:
            logger.log("ℹ️ Processed users data not found in cache, creating it...", 3)
            optimize_data("users_data.csv")
            self.df_users = clean_units(read_parquet_data("users_data.parquet"))
            self.save_cache_to_disk("users_data_processed", self.df_users)

        # =============================================== TRANSACTIONS ===============================================

        # Check if transactions_data_processed.parquet exists in data/cache directory and load it if it does
        # if not run optimize data, clean units and process_transaction data
        transactions_processed_path = self.cache_dir / "transactions_data_processed.parquet"
        transactions_to_del_path = self.cache_dir / "transactions_data.parquet"

        if transactions_processed_path.exists():
            logger.log(f"ℹ️ Loading processed transactions data from cache: {transactions_processed_path}", 3)
            self.df_transactions = pd.read_parquet(transactions_processed_path)

            if transactions_to_del_path.exists():
                os.remove(transactions_to_del_path)
                logger.log(f"🗑️ Deleted: {transactions_to_del_path}", 3)

        else:
            logger.log("ℹ️ Processed transactions data not found in cache, creating it...", 3)
            optimize_data("transactions_data.csv")
            self.df_transactions = clean_units(read_parquet_data("transactions_data.parquet", num_rows=num_rows))
            # Process transaction data (add latitude/longitude and state_name)
            self.df_transactions = self.process_transaction_data(self.df_transactions)
            self.save_cache_to_disk("transactions_data_processed", self.df_transactions)

        set_minor_merchants_threshold(transactions_processed_path)

        # =============================================== CARDS ===============================================

        # Check if cards_data_processed.parquet exists in data/cache directory and load it if it does
        # if not run optimize data and clean units
        cards_processed_path = self.cache_dir / "cards_data_processed.parquet"
        cards_to_del_path = self.cache_dir / "cards_data.parquet"

        if cards_processed_path.exists():
            logger.log(f"ℹ️ Loading processed cards data from cache: {cards_processed_path}", 3)
            self.df_cards = pd.read_parquet(cards_processed_path)

            if cards_to_del_path.exists():
                os.remove(cards_to_del_path)
                logger.log(f"🗑️ Deleted: {cards_to_del_path}", 3)

        else:
            logger.log("ℹ️ Processed cards data not found in cache, creating it...", 3)
            optimize_data("cards_data.csv")
            self.df_cards = clean_units(read_parquet_data("cards_data.parquet"))
            self.save_cache_to_disk("cards_data_processed", self.df_cards)

        # Convert to int once
        self.df_mcc["mcc"] = self.df_mcc["mcc"].astype(int)

        bm.print_time(level=4, add_empty_line=True)

    def save_cache_to_disk(self, cache_name, data):
        """
        Save a cache object to disk.

        Args:
            cache_name (str): Name of the cache file (without extension)
            data: The data to cache (DataFrame or dictionary)
        """
        try:
            cache_path = self.cache_dir / f"{cache_name}"

            if isinstance(data, pd.DataFrame):
                # Save DataFrame as parquet
                data.to_parquet(f"{cache_path}.parquet", index=False)
                logger.log(f"✅ Saved DataFrame cache to {cache_path}.parquet", indent_level=3)
            else:
                # Save other objects using pickle
                with open(f"{cache_path}.pkl", 'wb') as f:
                    pickle.dump(data, f)
                logger.log(f"✅ Saved object cache to {cache_path}.pkl", indent_level=3)

            return True
        except Exception as e:
            logger.log(f"⚠️ Failed to save cache {cache_name}: {str(e)}", indent_level=3)
            return False

    def load_cache_from_disk(self, cache_name, is_dataframe=True):
        """
        Load a cache object from disk.

        Args:
            cache_name (str): Name of the cache file (without extension)
            is_dataframe (bool): Whether the cache is a DataFrame (True) or other object (False)

        Returns:
            The cached data if successful, None otherwise
        """
        try:
            if is_dataframe:
                cache_path = self.cache_dir / f"{cache_name}.parquet"
                if cache_path.exists():
                    data = pd.read_parquet(cache_path)
                    logger.log(f"✅ Loaded DataFrame cache from {cache_path}", indent_level=3)
                    return data
            else:
                cache_path = self.cache_dir / f"{cache_name}.pkl"
                if cache_path.exists():
                    with open(cache_path, 'rb') as f:
                        data = pickle.load(f)
                    logger.log(f"✅ Loaded object cache from {cache_path}", indent_level=3)
                    return data

            return None
        except Exception as e:
            logger.log(f"⚠️ Failed to load cache {cache_name}: {str(e)}", indent_level=3)
            return None

    def process_transaction_data(self, df_transactions) -> pd.DataFrame:
        """
        Process transaction data by standardizing ZIP codes and mapping state abbreviations to full names.

        Args:
            df_transactions (pd.DataFrame): The transactions DataFrame to process

        Returns:
            pd.DataFrame: The processed transactions DataFrame
        """
        # Process transaction zip codes
        if not {"latitude", "longitude"}.issubset(df_transactions):
            logger.log("🔄 Home: Processing transaction zip codes...", 3)
            bm = Benchmark("Home: Processing transaction zip codes")

            # Create a copy to avoid modifying the original
            df = df_transactions.copy()

            df["zip"] = (
                df["zip"]
                .fillna(00000)  # When null
                .astype(int)  # 60614.0 -> 60614
                .astype(str)  # 60614 -> "60614"
                .str.zfill(5)  # "1234" -> "01234"
            )

            geo = self.nomi.query_postal_code(df["zip"].tolist())
            df["latitude"] = pd.to_numeric(geo["latitude"], errors="coerce").values
            df["longitude"] = pd.to_numeric(geo["longitude"], errors="coerce").values

            # Write back to parquet
            df.to_parquet(
                CACHE_DIRECTORY / "transactions_data.parquet",
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            bm.print_time(level=3)
            df_transactions = df
        else:
            logger.log("ℹ️ Home: Latitude/Longitude already exist, skipping geocoding", 3)

        # Creates a 'state_name' column from the 'merchant_state' column (abbreviated state names)
        if "state_name" not in df_transactions.columns:
            logger.log("🔄 Home: Mapping transaction state abbreviations to full names...", 3)
            bm = Benchmark("Home: Mapping transaction state abbreviations to full names")

            # Build mapping from abbreviation to full state name
            mapping = {s.abbr: s.name for s in us.states.STATES}

            # Create a copy to avoid modifying the original
            df = df_transactions.copy()

            # Map merchant_state (e.g. "NY") to full name (e.g. "New York")
            df["state_name"] = df["merchant_state"].map(mapping)

            # Null value -> Online
            df["state_name"] = df["state_name"].fillna("ONLINE")

            # Write back to parquet
            df.to_parquet(
                CACHE_DIRECTORY / "transactions_data.parquet",
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            bm.print_time(level=3)
            df_transactions = df
        else:
            logger.log("ℹ️ Home: State names already exist, skipping mapping", 3)

        return df_transactions

    def prepare_shared_data(self):
        """
        Prepares shared data that is used by multiple tabs.
        This avoids duplicate processing and improves performance.

        Creates:
            - transactions_mcc: DataFrame with transactions joined with MCC codes
            - transactions_mcc_users: DataFrame with transactions joined with MCC codes and users
        """
        logger.log("ℹ️ DataManager: Preparing shared data for tabs...", indent_level=2)
        bm = Benchmark("DataManager: Shared data preparation")

        # Try to load cached data first
        cached_transactions_mcc = self.load_cache_from_disk("transactions_mcc")
        cached_transactions_mcc_users = self.load_cache_from_disk("transactions_mcc_users")

        if cached_transactions_mcc is not None and cached_transactions_mcc_users is not None:
            self.transactions_mcc = cached_transactions_mcc
            self.transactions_mcc_users = cached_transactions_mcc_users
            logger.log("✅ DataManager: Loaded shared data from cache", indent_level=3)
        else:
            logger.log("ℹ️ DataManager: Cache not found, preparing shared data...", indent_level=3)

            # Ensure transactions df has int mcc for efficient merging
            df_transactions = self.df_transactions
            if 'mcc' in df_transactions.columns and not pd.api.types.is_integer_dtype(df_transactions['mcc']):
                df_transactions = df_transactions.copy()
                df_transactions['mcc'] = df_transactions['mcc'].astype(int)
                self.df_transactions = df_transactions

            # Join transactions and mcc_codes using efficient merge
            self.transactions_mcc = pd.merge(
                df_transactions,
                self.df_mcc,
                how="left",
                on="mcc",
                sort=False  # Avoid unnecessary sorting
            )

            # Transactions join MCC join Users - use efficient merge
            self.transactions_mcc_users = pd.merge(
                self.transactions_mcc,
                self.df_users,
                how="left",
                left_on='client_id',
                right_on='id',
                sort=False  # Avoid unnecessary sorting
            )

            # Save the prepared data to cache
            self.save_cache_to_disk("transactions_mcc", self.transactions_mcc)
            self.save_cache_to_disk("transactions_mcc_users", self.transactions_mcc_users)

        bm.print_time(level=3, add_empty_line=True)

    def _save_num_rows_to_cache(self, num_rows):
        """
        Save the num_rows value to a file in the cache directory.

        Args:
            num_rows: The number of rows value to save
        """
        try:
            cache_path = self.cache_dir / "num_rows.pkl"
            with open(cache_path, 'wb') as f:
                pickle.dump(num_rows, f)
            logger.log(f"✅ Saved num_rows value to {cache_path}", indent_level=3)
            self._cached_num_rows = num_rows
            return True
        except Exception as e:
            logger.log(f"⚠️ Error saving num_rows value: {str(e)}", indent_level=3)
            return False

    def _load_num_rows_from_cache(self):
        """
        Load the num_rows value from a file in the cache directory.

        Returns:
            The num_rows value if the file exists, None otherwise
        """
        try:
            cache_path = self.cache_dir / "num_rows.pkl"
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    num_rows = pickle.load(f)
                logger.log(f"✅ Loaded num_rows value from {cache_path}: {num_rows:,}", indent_level=3)
                self._cached_num_rows = num_rows
                return num_rows
            else:
                logger.log("ℹ️ No cached num_rows value found", indent_level=3)
                return None
        except Exception as e:
            logger.log(f"⚠️ Error loading num_rows value: {str(e)}", indent_level=3)
            return None

    def _delete_cache_directory(self):
        """
        Delete the entire cache directory and recreate it.
        """
        import shutil
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                logger.log(f"🗑️ Deleted cache directory: {self.cache_dir}", indent_level=3)
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.log(f"ℹ️ Created new cache directory: {self.cache_dir}", indent_level=3)
            return True
        except Exception as e:
            logger.log(f"⚠️ Error deleting cache directory: {str(e)}", indent_level=3)
            return False

    def _delete_unneeded_files(self):
        """
        Deletes unneeded temporary files to free up disk space. This is used to remove
        specific files within the cache directory that are no longer required by the
        application.

        Raises:
            Any error raised by `pathlib.Path.unlink` if deletion of a file fails.
        """
        paths_to_delete = (
            self.cache_dir / "users_data.parquet",
            self.cache_dir / "transactions_data.parquet",
            self.cache_dir / "cards_data.parquet"
        )

        for path in paths_to_delete:
            if path.exists():
                path.unlink()  # If the path is a pathlib.Path, which it is in this case (DATA_DIRECTORY)
                logger.log(f"🗑️ Deleted unneeded temporary file: {path}", 3)

    def start(self, num_rows=50_000):
        """
        Starts the data loading and caching flow, which involves multiple stages such as loading
        data frames, checking and utilizing the cache, creating cache if required, and finalizing
        other setups like cleaning unneeded files and initializing a geometric shape.

        Args:
            num_rows (int, optional): Number of rows to load and cache when no cache exists.
                When cache exists, the entire cache is loaded. Defaults to 100_000.

        The method ensures:
        - Proper fallback to normal initialization if cache loading fails.
        - Attempting cache creation when it does not already exist.
        - Cleaning up unnecessary files as part of the finalization.
        - If num_rows changes from a previous run, the cache is deleted and recreated.

        Raises:
            RuntimeError: If the cache creation process fails.

        Attributes:
            online_shape: Represents a geometric rounded rectangle with a predefined set of
            coordinates and styling properties.
        """
        # First, load the basic data frames regardless of cache
        # This is needed for both cached and non-cached paths
        self.load_data_frames(num_rows=num_rows)

        # Check if cache exists and load from it if it does
        if self.data_cacher.cache_exists():
            logger.log("ℹ️ DataManager: Cache exists, loading data from cache...", indent_level=2)
            if self.data_cacher.load_from_cache():
                logger.log("✅ DataManager: Successfully loaded data from cache", indent_level=2)
            else:
                logger.log("⚠️ DataManager: Failed to load from cache, falling back to normal initialization",
                           indent_level=2)
                if not self.data_cacher.create_cache():
                    logger.log("❌ DataManager: Failed to create cache", indent_level=2)
        else:
            logger.log("ℹ️ DataManager: Cache does not exist, creating cache...", indent_level=2)
            if not self.data_cacher.create_cache():
                logger.log("❌ DataManager: Failed to create cache", indent_level=2)

        self._delete_unneeded_files()

        # Set up the online shape (this is quick and doesn't need caching)
        self.online_shape = rounded_rect(
            l=-95, b=23, r=-85, t=28,
            radius=0.7,
            n_arc=8
        )
