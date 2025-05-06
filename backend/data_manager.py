from pathlib import Path

import pandas as pd
import pgeocode
import us

import utils.logger as logger
from backend.data_handler import optimize_data, clean_units, json_to_data_frame
from utils.benchmark import Benchmark

DATA_DIRECTORY = Path("assets/data/")


def _read_parquet_data(file_name: str, sort_alphabetically: bool = False) -> pd.DataFrame:
    """
    Reads a Parquet file and loads it into a Pandas DataFrame. Optionally sorts the columns
    alphabetically if specified.

    Arguments:
        file_name (str): The name of the Parquet file to be read. The file must exist
            in the predefined data directory.
        sort_alphabetically (bool): Optional; whether to sort the DataFrame's columns
            alphabetically. Defaults to False.

    Returns:
        pd.DataFrame: The loaded data in a Pandas DataFrame format.

    Raises:
        FileNotFoundError: If the specified file does not exist in the data directory.
    """
    file_path = DATA_DIRECTORY / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"⚠️ Parquet file not found: {file_path}")

    data_frame = pd.read_parquet(file_path, engine="pyarrow")

    if sort_alphabetically:
        data_frame = data_frame.reindex(sorted(data_frame.columns), axis=1)

    return data_frame


class DataManager:
    """
    Manages data loading, cleaning, and transformation processes.

    DataManager centralizes the management of user, transaction, and card datasets. It handles the initialization
    of datasets, including loading raw data, transforming it to predefined formats, and carrying out basic data
    cleaning operations. This class is aimed for use in scenarios requiring pre-processed data as DataFrames.
    """

    def __init__(self, data_dir: Path = DATA_DIRECTORY):
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

        self.initialize()
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

    def initialize(self):
        """
        Initializes and prepares data for further processing by converting CSV files to parquet files,
        loading them as DataFrames, and performing cleaning and preprocessing tasks such as processing
        zip codes and state names for transactions. Additionally, it logs a summary of the processed data
        units.

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
