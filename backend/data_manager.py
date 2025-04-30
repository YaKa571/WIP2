from pathlib import Path

import pandas as pd

from backend.data_handler import optimize_data, clean_units, json_to_data_frame

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
    def __init__(self, data_dir: Path = DATA_DIRECTORY):
        self.data_dir = data_dir
        self.df_users = None
        self.units_users = None
        self.df_transactions = None
        self.units_transactions = None
        self.df_cards = None
        self.units_cards = None
        self.df_mcc = None
        self.df_train_fraud = None

    def load_all(self):
        # Converts CSV files to parquet files if they don't exist yet and load them as DataFrames
        optimize_data("users_data.csv", "transactions_data.csv", "cards_data.csv")

        # Read and clean data – clean_units returns (df, unit_info)
        self.df_users, self.units_users = clean_units(_read_parquet_data("users_data.parquet"))
        self.df_transactions, self.units_transactions = clean_units(_read_parquet_data("transactions_data.parquet"))
        self.df_cards, self.units_cards = clean_units(_read_parquet_data("cards_data.parquet"))
        self.df_mcc = json_to_data_frame("mcc_codes.json")
        # TODO: Too slow --> self.df_train_fraud = json_to_data_frame("train_fraud_labels.json")

        # Print summary
        print(f"\nℹ️ Users: {self.units_users}\nℹ️ Transactions: {self.units_transactions}\nℹ️ Cards: {self.units_cards}\n")
