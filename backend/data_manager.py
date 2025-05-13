from pathlib import Path

import pandas as pd
import pgeocode
import pyarrow as pa
import us
from pyarrow.parquet import ParquetFile

import utils.logger as logger
from backend.data_handler import optimize_data, clean_units, json_to_data_frame, json_to_dict, \
    get_mcc_description_by_merchant_id
from backend.kpi_models import HomeKPIs, MerchantKPI, VisitKPI, UserKPI
from utils.benchmark import Benchmark

DATA_DIRECTORY = Path("assets/data/")


def _read_parquet_data(file_name: str, num_rows: int = None, sort_alphabetically: bool = False) -> pd.DataFrame:
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
        df = pa.Table.from_batches(batches=[batch]).to_pandas()

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
        self.df_users: pd.DataFrame = pd.DataFrame()
        self.units_users: dict = {}
        self.df_transactions: pd.DataFrame = pd.DataFrame()
        self.units_transactions: dict = {}
        self.df_cards: pd.DataFrame = pd.DataFrame()
        self.units_cards: dict = {}
        self.df_mcc: pd.DataFrame = pd.DataFrame()
        self.df_train_fraud: pd.DataFrame = pd.DataFrame()

        self.amount_of_transactions: int = 0
        self.sum_of_transactions: float = 0.00
        self.avg_transaction_amount: float = 0.00

        self._nomi = pgeocode.Nominatim("us")

        self.mcc_dict = json_to_dict("mcc_codes.json")

        self.home_kpi = HomeKPIs(
            most_valuable_merchant=MerchantKPI(0, 0, "Undefined", "0,00"),
            most_visited_merchant=VisitKPI(0, 0, "Undefined", "0"),
            top_spending_user=UserKPI(0, "Undefined", 0, "0,00"),
            most_frequent_user=UserKPI(0, "Undefined", 0, "0,00"),
        )

        self.start()  # <-- Initializing all data
        benchmark_data_manager.print_time()

    def _process_transaction_zips(self):
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

    def _process_transaction_states(self):
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

    def _process_transaction_data(self):
        # Process transaction zip codes
        self._process_transaction_zips()

        # Creates a 'state_name' column from the 'merchant_state' column (abbreviated state names)
        self._process_transaction_states()

    def _calc_most_valuable_merchant(self) -> None:
        """
        Calculate and update the most valuable merchant details in the home_kpi dictionary.

        This method analyzes transaction data to determine details of the merchant with the
        highest transaction sum. It then updates the information including merchant ID, MCC code,
        MCC description, and the transaction value formatted in US style into the `home_kpi`
        dictionary under the key `most_valuable_merchant`. The method relies on the provided
        transaction DataFrame and MCC dictionary.
        """
        df_sums = (
            self.df_transactions
            .groupby(["merchant_id", "mcc"])["amount"]
            .sum()
            .to_frame("merchant_sum")  # Convert to DataFrame
            .reset_index()  # merchant_id as index
        )

        # Find the row with the highest merchant_sum
        idx_top = df_sums["merchant_sum"].idxmax()
        top_row = df_sums.loc[idx_top]

        # Extract values
        merchant_id = int(top_row["merchant_id"])
        mcc = top_row["mcc"]
        mcc_desc = get_mcc_description_by_merchant_id(self.mcc_dict, mcc)
        value = float(top_row["merchant_sum"])

        # Write to dict
        self.home_kpi.most_valuable_merchant = MerchantKPI(
            id=merchant_id,
            mcc=int(top_row["mcc"]),
            mcc_desc=mcc_desc,
            value="{:,.2f}".format(value)
        )

    def _calc_most_valuable_user(self) -> None:
        """
        Calculates and updates the most valuable user based on transaction data.

        The method identifies the client with the highest transaction sum from the
        provided transaction dataframe. It retrieves the client's details, such as
        ID, gender, and current age, by matching the client ID with the users' dataframe.
        The method updates the most valuable user's information as a `UserKPI` object
        in the `home_kpi.top_spending_user` attribute.
        """
        df_sums = (
            self.df_transactions
            .groupby("client_id")["amount"]
            .sum()
            .to_frame("client_sum")
            .reset_index()
        )

        idx_top = df_sums["client_sum"].idxmax()
        top_row = df_sums.loc[idx_top]

        client_id = int(top_row["client_id"])
        client_sum = float(top_row["client_sum"])

        client_gender = self.df_users[self.df_users["id"] == client_id]["gender"].values[0]
        client_current_age = self.df_users[self.df_users["id"] == client_id]["current_age"].values[0]

        self.home_kpi.top_spending_user = UserKPI(
            id=client_id,
            gender=client_gender,
            current_age=client_current_age,
            value="{:,.2f}".format(client_sum)
        )

    def _calc_most_visited_merchant(self) -> None:
        """
        Calculates the most visited merchant from transaction data and updates the home KPI
        with details of the most visited merchant, including its ID, visit count, MCC code,
        and MCC description. This method operates on the dataframe containing transaction
        data and relies on external utility functions and objects for MCC description and
        home KPI updates.
        """
        column = self.df_transactions["merchant_id"]

        most_visited_merchant_id = column.value_counts().idxmax()
        visits = column.value_counts().max()

        top_rows = self.df_transactions[self.df_transactions["merchant_id"] == most_visited_merchant_id]
        top_row = top_rows.iloc[0]

        mcc = top_row["mcc"]
        mcc_desc = get_mcc_description_by_merchant_id(self.mcc_dict, mcc)

        self.home_kpi.most_visited_merchant = VisitKPI(
            id=most_visited_merchant_id,
            visits="{:,}".format(visits).replace(",", "."),
            mcc=mcc,
            mcc_desc=mcc_desc
        )

    def _calc_home_tab_kpis(self):
        """
        Calculates Key Performance Indicators (KPIs) for the home tab view.

        This function performs the computation of essential metrics displayed on a
        home tab interface, including calculations for determining the merchant with
        the highest value.
        """
        self._calc_most_valuable_merchant()
        self._calc_most_visited_merchant()
        self._calc_most_valuable_user()
        # TODO: Add remaining KPIs

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
        self.df_transactions, self.units_transactions = clean_units(_read_parquet_data("transactions_data.parquet",
                                                                                       num_rows=500_000))
        self.df_cards, self.units_cards = clean_units(_read_parquet_data("cards_data.parquet"))
        self.df_mcc = json_to_data_frame("mcc_codes.json")
        # TODO: Too slow --> self.df_train_fraud = json_to_data_frame("train_fraud_labels.json")

        # Process transaction_data.parquet file
        self._process_transaction_data()

        # Calculate KPIs for Home Tab
        self._calc_home_tab_kpis()

        # Calculations
        self.amount_of_transactions = len(self.df_transactions)
        self.sum_of_transactions = self.df_transactions["amount"].sum()
        self.avg_transaction_amount = self.sum_of_transactions / self.amount_of_transactions

        # Print summary
        logger.log(f"ℹ️ Users: {self.units_users}", 1)
        logger.log(f"ℹ️ Transactions: {self.units_transactions}", 1)
        logger.log(f"ℹ️ Cards: {self.units_cards}\n", 1)
