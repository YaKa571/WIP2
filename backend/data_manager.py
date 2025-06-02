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
    def initialize(data_dir: Path = DATA_DIRECTORY):
        if DataManager._instance is None:
            DataManager._instance = DataManager(data_dir)

    @staticmethod
    def get_instance():
        if DataManager._instance is None:
            raise Exception("⚠️ DataManager has not been initialized. Call DataManager.initialize() first.")
        return DataManager._instance

    def __init__(self, data_dir: Path = DATA_DIRECTORY):
        if DataManager._instance is not None:
            raise Exception("⚠️ Use DataManager.get_instance() instead of creating a new instance.")

        benchmark_data_manager = Benchmark("DataManager initialization")
        logger.log("ℹ️ Initializing DataManager...", indent_level=1)

        self.data_dir = data_dir
        self.cache_dir = data_dir / "cache"

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
        self.start()
        benchmark_data_manager.print_time()

    def load_data_frames(self):
        """
        Loads and pre-processes the data from specified files to use them as DataFrames. This includes
        optimizing data storage by converting CSV files to parquet format if such files do not exist,
        cleaning the data, and loading it into pandas DataFrames. Additionally, MCC codes are converted
        from a JSON file into a DataFrame.

        Raises:
            FileNotFoundError: If any of the specified files are not found during processing.
        """
        logger.log("ℹ️ DataManager: Loading from files...", 2, add_line_before=True)
        bm = Benchmark("DataManager: Loading from files")

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
            self.df_transactions = clean_units(read_parquet_data("transactions_data.parquet"))
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

    def start(self):
        """
        Starts the initialization process for various components and performs
        data calculations for key metrics.

        This method is responsible for initializing components related
        to the home and user tabs by loading data into their respective
        classes and running their setup methods. Additionally, it
        performs calculations on transaction data to determine metrics
        such as the total number, the sum, and the average amount of
        transactions. A graphical shape is also predefined.

        If a cache exists, the data is loaded from the cache instead of
        being processed from scratch, which significantly improves startup time.

        Raises
        ------
        KeyError
            If required keys are missing in the data frames during initialization.

        Attributes
        ----------
        home_tab_data : HomeTabData
            Stores and manages data related to the home tab operations.
        user_tab_data : UserTabData
            Stores and manages data related to the user tab operations.
        amount_of_transactions : int
            Total count of transactions loaded into the system.
        sum_of_transactions : float
            The total sum of all transaction amounts.
        avg_transaction_amount : float
            The average amount of transactions calculated.
        online_shape : Shape
            Predefined rounded rectangular shape for graphical visualization.
        """
        # First, load the basic data frames regardless of cache
        # This is needed for both cached and non-cached paths
        self.load_data_frames()

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

        # Set up the online shape (this is quick and doesn't need caching)
        self.online_shape = rounded_rect(
            l=-95, b=23, r=-85, t=28,
            radius=0.7,
            n_arc=8
        )
