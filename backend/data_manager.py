from pathlib import Path
from typing import Optional

import pandas as pd
import pgeocode

import utils.logger as logger
from backend.data_handler import optimize_data, clean_units, json_to_data_frame, json_to_dict, \
    read_parquet_data
from backend.data_setup.tabs.tab_cluster_data import ClusterTabData
from backend.data_setup.tabs.tab_home_data import HomeTabData
from backend.data_setup.tabs.tab_merchant_data import MerchantTabData
from backend.data_setup.tabs.tab_user_data import UserTabData
from components.constants import DATA_DIRECTORY
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
        self.df_users: pd.DataFrame = pd.DataFrame()
        self.df_transactions: pd.DataFrame = pd.DataFrame()
        self.df_cards: pd.DataFrame = pd.DataFrame()
        self.df_mcc: pd.DataFrame = pd.DataFrame()
        self.df_train_fraud: pd.DataFrame = pd.DataFrame()

        self.amount_of_transactions: int = 0
        self.sum_of_transactions: float = 0.00
        self.avg_transaction_amount: float = 0.00

        self.nomi = pgeocode.Nominatim("us")

        self.mcc_dict = json_to_dict("mcc_codes.json")

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

    # User Tab

    def load_data_frames(self):
        """
        Loads and pre-processes the data from specified files to use them as DataFrames. This includes
        optimizing data storage by converting CSV files to parquet format if such files do not exist,
        cleaning the data, and loading it into pandas DataFrames. Additionally, MCC codes are converted
        from a JSON file into a DataFrame.

        Raises:
            FileNotFoundError: If any of the specified files are not found during processing.
        """
        # Converts CSV files to parquet files if they don't exist yet and load them as DataFrames
        optimize_data("users_data.csv", "transactions_data.csv", "cards_data.csv")

        # Read and clean data
        self.df_users = clean_units(read_parquet_data("users_data.parquet"))
        self.df_transactions = clean_units(read_parquet_data("transactions_data.parquet",
                                                             num_rows=100_000))
        self.df_cards = clean_units(read_parquet_data("cards_data.parquet"))
        self.df_mcc = json_to_data_frame("mcc_codes.json")

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
        self.load_data_frames()

        # Initialize Home Tab Data
        self.home_tab_data = HomeTabData(self)
        self.home_tab_data.initialize()

        # Initialize Merchant Tab Data
        self.merchant_tab_data = MerchantTabData(self)
        self.merchant_tab_data.initialize()

        # Initialize Cluster Tab Data
        self.cluster_tab_data = ClusterTabData(self)
        self.cluster_tab_data.initialize()

        # Initialize User Tab Data
        self.user_tab_data = UserTabData(self)
        self.user_tab_data.initialize()

        # Calculations
        self.amount_of_transactions = len(self.df_transactions)
        self.sum_of_transactions = self.df_transactions["amount"].sum()
        self.avg_transaction_amount = self.sum_of_transactions / self.amount_of_transactions
        self.online_shape = rounded_rect(
            l=-95, b=23, r=-85, t=28,
            radius=0.7,
            n_arc=8
        )
