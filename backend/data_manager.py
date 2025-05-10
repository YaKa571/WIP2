from pathlib import Path

import pandas as pd
import pgeocode
import pyarrow as pa
import us
from pyarrow.parquet import ParquetFile

import utils.logger as logger
from backend.data_handler import optimize_data, clean_units, json_to_data_frame
from utils.benchmark import Benchmark

DATA_DIRECTORY = Path("assets/data/")


def _read_parquet_data(file_name: str, num_rows: int = 500_000, sort_alphabetically: bool = False) -> pd.DataFrame:
    """
    Reads a Parquet file into a pandas DataFrame.

    This function loads data from a specified Parquet file, with options to limit the
    number of rows and to sort column names alphabetically.

    Parameters:
    file_name: str
        The name of the Parquet file to read. Must exist in the DATA_DIRECTORY.
    num_rows: int, optional
        The number of rows to load from the Parquet file. By default, 500,000 rows
        are loaded. If None or greater than the total number of rows in the file,
        all rows will be loaded.
    sort_alphabetically: bool, optional
        If True, sort the column names alphabetically. Default is False.

    Returns:
    pd.DataFrame
        The pandas DataFrame containing the data from the Parquet file.

    Raises:
    FileNotFoundError
        If the specified file does not exist in the DATA_DIRECTORY.
    """
    file_path = DATA_DIRECTORY / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"⚠️ Parquet file not found: {file_path}")

    pf = ParquetFile(file_path)
    total_rows = pf.metadata.num_rows

    if num_rows is None or num_rows >= total_rows:
        df = pd.read_parquet(file_path, engine="pyarrow")
    else:
        batch = next(pf.iter_batches(batch_size=num_rows))
        df = pa.Table.from_batches([batch]).to_pandas()

    if sort_alphabetically:
        df = df.reindex(sorted(df.columns), axis=1)

    return df


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
        logger.log("\nℹ️ Initializing DataManager...")

        self.data_dir = data_dir
        self.df_users = None
        self.units_users = None
        self.df_transactions = None
        self.units_transactions = None
        self.df_cards = None
        self.units_cards = None
        self.df_mcc = None
        self.df_train_fraud = None

        self.amount_of_transactions = None
        self.sum_of_transactions = None
        self.avg_transaction_amount = None

        self._nomi = pgeocode.Nominatim("us")

        self.start()  # <-- Initializing all data
        benchmark_data_manager.print_time()

    def process_transaction_zips(self):
        """
        Processes zip codes in the transactions DataFrame.

        This function standardizes transaction ZIP codes by handling missing values,
        converting data types, and ensuring all ZIP codes are represented as 5-digit
        strings. Missing values are filled with '0', decimal ZIP codes are converted
        to integers, and string representation of ZIP codes is padded with zeros
        to reach 5 digits.
        """
        if not {"latitude", "longitude"}.issubset(self.df_transactions):
            logger.log("🔄 Processing transaction zip codes...", 1)

            df = self.df_transactions.copy()

            df["zip"] = (
                df["zip"]
                .fillna(00000)  # When null
                .astype(int)  # 60614.0 -> 60614
                .astype(str)  # 60614 -> "60614"
                .str.zfill(5)  # "1234" -> "01234"
            )

            geo = self._nomi.query_postal_code(df["zip"].tolist())
            df["latitude"] = pd.to_numeric(geo["latitude"], errors="coerce").values
            df["longitude"] = pd.to_numeric(geo["longitude"], errors="coerce").values

            # Write back to parquet
            df.to_parquet(
                DATA_DIRECTORY / "transactions_data.parquet",
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            # Update in-memory DataFrame
            self.df_transactions = df
        else:
            logger.log("ℹ️ Latitude/Longitude already exist, skipping geocoding", 1)

    def process_transaction_states(self):
        """
        Processes transaction states by mapping state abbreviations to their full names. If the
        state names are already present in the DataFrame, the method skips the mapping process.
        Otherwise, it maps abbreviations to full state names, writes the updated data to a Parquet
        file, and updates the in-memory DataFrame.

        Raises
        ------
        None
        """
        if "state_name" not in self.df_transactions.columns:
            logger.log("🔄 Mapping transaction state abbreviations to full names...", 1)

            # Build mapping from abbreviation to full state name
            mapping = {s.abbr: s.name for s in us.states.STATES}

            df = self.df_transactions.copy()
            # Map merchant_state (e.g. "NY") to full name (e.g. "New York")
            df["state_name"] = df["merchant_state"].map(mapping)

            # Write back to parquet
            df.to_parquet(
                DATA_DIRECTORY / "transactions_data.parquet",
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            # Update in-memory DataFrame
            self.df_transactions = df
        else:
            logger.log("ℹ️ State names already exist, skipping mapping", 1)

    def start(self):
        """
        Starts the process of loading, cleaning, and processing transaction data. The method primarily deals
        with converting raw data files to optimized formats, reading the data as DataFrames, and performing
        initial preprocessing steps. It also calculates summary statistics such as the total number,
        sum, and average of transaction amounts and logs key insights about the processed data.

        Summary:
        1. Converts source CSV files to parquet format if not done previously.
        2. Reads the converted parquet files into DataFrames.
        3. Cleans data and retrieves associated unit information.
        4. Reads a JSON file for MCC codes into a DataFrame.
        5. Processes transaction-specific details such as zip codes and state names.
        6. Logs a summary of the processed data units.

        Returns:
            None
        """
        # Converts CSV files to parquet files if they don't exist yet and load them as DataFrames
        optimize_data("users_data.csv", "transactions_data.csv", "cards_data.csv")

        # Read and clean data – clean_units returns (df, unit_info)
        self.df_users, self.units_users = clean_units(_read_parquet_data("users_data.parquet"))
        self.df_transactions, self.units_transactions = clean_units(_read_parquet_data("transactions_data.parquet"))
        self.df_cards, self.units_cards = clean_units(_read_parquet_data("cards_data.parquet"))
        self.df_mcc = json_to_data_frame("mcc_codes.json")
        # TODO: Too slow --> self.df_train_fraud = json_to_data_frame("train_fraud_labels.json")

        # Process transaction zip codes
        self.process_transaction_zips()

        # Creates a 'state_name' column from the 'merchant_state' column (abbreviated state names)
        self.process_transaction_states()

        # Calculations
        self.amount_of_transactions = len(self.df_transactions)
        self.sum_of_transactions = self.df_transactions["amount"].sum()
        self.avg_transaction_amount = self.sum_of_transactions / self.amount_of_transactions

        # Print summary
        logger.log(f"ℹ️ Users: {self.units_users}", 1)
        logger.log(f"ℹ️ Transactions: {self.units_transactions}", 1)
        logger.log(f"ℹ️ Cards: {self.units_cards}\n", 1)
