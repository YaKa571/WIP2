from pathlib import Path

import pandas as pd
import pgeocode
import pyarrow as pa
import us
from pyarrow.parquet import ParquetFile

import utils.logger as logger
from backend.data_handler import optimize_data, clean_units, json_to_data_frame, json_to_dict, \
    get_mcc_description_by_merchant_id
from backend.kpi_models import MerchantKPI, VisitKPI, UserKPI, PeakHourKPI
from utils.benchmark import Benchmark

DATA_DIRECTORY = Path("assets/data/")


# TODO: @Diego: Move home-tab-related methods into home tab class
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
        logger.log("ℹ️ Initializing DataManager...", indent_level=1)

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

        self._cache_most_valuable_merchant: dict[str | None, MerchantKPI] = {}
        self._cache_most_visited_merchant: dict[str | None, VisitKPI] = {}
        self._cache_top_spending_user: dict[str | None, UserKPI] = {}
        self._cache_peak_hour: dict[str | None, PeakHourKPI] = {}
        self._cache_expenditures_by_gender: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_age: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_channel: dict[str | None, dict[str, float]] = {}

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
            logger.log("🔄 Processing transaction zip codes...", 2)
            bm = Benchmark("Processing")

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
            bm.print_time(level=3)
        else:
            logger.log("ℹ️ Latitude/Longitude already exist, skipping geocoding", 2)

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
            logger.log("🔄 Mapping transaction state abbreviations to full names...", 2)
            bm = Benchmark("Mapping")

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
            bm.print_time(level=3)
        else:
            logger.log("ℹ️ State names already exist, skipping mapping", 2)

    def _process_transaction_data(self) -> None:
        # Process transaction zip codes
        self._process_transaction_zips()

        # Creates a 'state_name' column from the 'merchant_state' column (abbreviated state names)
        self._process_transaction_states()

    def get_most_valuable_merchant(self, state: str = None) -> MerchantKPI:
        """
        Gets the most valuable merchant based on transaction amounts. The method
        can fetch results for all states or filter data by a specific state if
        provided. Results are cached for efficiency when the same state data is
        requested repeatedly.

        Parameters:
        state: str, optional
            The state name to filter transactions. If None, data from all states
            is considered.

        Returns:
        MerchantKPI
            The MerchantKPI object containing details of the most valuable
            merchant, including its ID, MCC, MCC description, and total transaction
            value.
        """
        # Cache-Check
        if state in self._cache_most_valuable_merchant:
            return self._cache_most_valuable_merchant[state]

        # Compute if not cached
        df = self.df_transactions.copy()
        if state:
            df = df[df["state_name"] == state]

        # Ensure we work on a copy
        df = df.copy()
        df_sums = (
            df.groupby(["merchant_id", "mcc"])["amount"]
            .sum()
            .reset_index(name="merchant_sum")
        )
        top = df_sums.loc[df_sums["merchant_sum"].idxmax()]

        kpi = MerchantKPI(
            id=int(top["merchant_id"]),
            mcc=int(top["mcc"]),
            mcc_desc=get_mcc_description_by_merchant_id(self.mcc_dict, int(top["mcc"])),
            value=f"{float(top['merchant_sum']):,.2f}"
        )

        # Cache & return
        self._cache_most_valuable_merchant[state] = kpi
        return kpi

    def get_peak_hour(self, state: str = None) -> PeakHourKPI:
        """
        Determines the hour with the highest number of transactions from the given data, optionally
        filtering transactions by state. The resulting information is cached for future calls to
        optimize performance.

        Attributes:
            _cache_peak_hour: A dictionary used to store cached results of peak hour calculations
                for each state for quick future references.
            df_transactions: A DataFrame containing transaction data with "date" and "state_name"
                columns.

        Args:
            state: str, optional
                The name of the state to filter transactions by, or None to include all transactions.

        Returns:
            PeakHourKPI
                An object containing the hour range with the most transactions and the formatted count
                of these transactions. The hour range is formatted as "HH:00 – HH:00", ensuring
                a 24-hour time format.
        """
        # Cache-Check
        if state in self._cache_peak_hour:
            return self._cache_peak_hour[state]

        # Filter transactions by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Ensure we work on a copy and parse dates
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["hour"] = df["date"].dt.hour

        # Count transactions per hour
        hour_counts = df["hour"].value_counts().sort_index()
        most_active_hour = hour_counts.idxmax()
        count = int(hour_counts.max())

        # Format results
        hour_str = f"{most_active_hour:02d}:00 – {(most_active_hour + 1) % 24:02d}:00"
        value_str = f"{count:,}".replace(",", ".")

        # Build the KPI object
        kpi = PeakHourKPI(hour_range=hour_str, value=value_str)

        # Cache & return
        self._cache_peak_hour[state] = kpi
        return kpi

    def get_top_spending_user(self, state: str = None) -> UserKPI:
        """
        Identifies and returns the user with the highest total spending within the dataset. If a state
        name is provided, the function filters the data by the specified state before determining the
        top spending user. The result is cached for future calls with the same state.

        Parameters:
        state: str, optional
            The name of the state to filter the transactions. If None, transactions from all states
            are considered.

        Returns:
        UserKPI
            An object containing details of the top spending user, including their ID, gender,
            current age, and a formatted string of their total spending.
        """
        # Cache-Check
        if state in self._cache_top_spending_user:
            return self._cache_top_spending_user[state]

        # Filter transactions by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Ensure we work on a copy and sum amounts per client
        df = df.copy()
        df_sums = (
            df.groupby("client_id")["amount"]
            .sum()
            .reset_index(name="client_sum")
        )

        # Identify top client
        idx_top = df_sums["client_sum"].idxmax()
        top = df_sums.loc[idx_top]
        client_id = int(top["client_id"])
        client_sum = float(top["client_sum"])

        # Lookup user details
        user_row = self.df_users.loc[self.df_users["id"] == client_id].iloc[0]
        gender = user_row["gender"]
        current_age = int(user_row["current_age"])

        # Build KPI object
        value_str = f"{client_sum:,.2f}"
        kpi = UserKPI(
            id=client_id,
            gender=gender,
            current_age=current_age,
            value=value_str
        )

        # Cache & return
        self._cache_top_spending_user[state] = kpi
        return kpi

    def get_most_visited_merchant(self, state: str = None) -> VisitKPI:
        """
        Returns the most visited merchant within the specified state or across all states if no state is
        specified. This method analyzes transaction data to determine the merchant with the highest visit
        count. Additionally, it retrieves the merchant's MCC and its description and formats the visit count
        as a string with dot-separated thousand delimiters.

        If data is already cached for the specified state, it retrieves the record directly from the cache
        for improved efficiency.

        Attributes:
            self.df_transactions (DataFrame): A DataFrame containing transaction data. Expected columns
                include 'state_name', 'merchant_id', and 'mcc'.
            self._cache_most_visited_merchant (dict): A cache to store previously computed results for
                faster retrieval. Keys are state names, and values are corresponding most-visited merchant data.
            self.mcc_dict (dict): A dictionary mapping MCC codes to their descriptions.

        Args:
            state (str, optional): The name of the state for which the most visited merchant is to be
                identified. Defaults to None, in which case all states are analyzed.

        Returns:
            VisitKPI: An object containing the most visited merchant's details, including their ID, MCC,
                MCC description, and formatted number of visits. Visit count is provided as a string with
                dots as thousand separators.
        """
        # Cache check
        if state in self._cache_most_visited_merchant:
            return self._cache_most_visited_merchant[state]

        # Filter by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Ensure we work on a copy and compute visit counts per merchant_id
        df = df.copy()
        vc = df["merchant_id"].value_counts()
        most_id = int(vc.idxmax())
        visits = int(vc.max())

        # Lookup MCC for this merchant
        #    we take the first matching row to get the mcc
        mcc = int(df.loc[df["merchant_id"] == most_id, "mcc"].iloc[0])
        mcc_desc = get_mcc_description_by_merchant_id(self.mcc_dict, mcc)

        # Format visits with dot as thousand separator
        visits_str = f"{visits:,}".replace(",", ".")

        # Build the KPI object
        kpi = VisitKPI(
            id=most_id,
            mcc=mcc,
            mcc_desc=mcc_desc,
            visits=visits_str
        )

        # Cache & return
        self._cache_most_visited_merchant[state] = kpi
        return kpi

    def _calc_home_tab_kpis(self):
        """
        Calculates the Key Performance Indicators (KPIs) required for the Home Tab. This function logs
        the start of the KPI calculation and uses benchmark tracking to log the time taken for the
        calculation process. It performs several operations to fetch specific KPI values related to
        merchants and users.
        """
        logger.log("ℹ️ Calculating KPIs for Home Tab...", 2)
        bm = Benchmark("Calculation")
        self.get_most_valuable_merchant()
        self.get_most_visited_merchant()
        self.get_top_spending_user()
        self.get_peak_hour()
        bm.print_time(level=3)

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

        # Copy & optional filter
        df = self.df_transactions.copy()
        if state:
            df = df[df["state_name"] == state]

        # Merge with user gender
        df_merged = pd.merge(
            df[["client_id", "amount"]],
            self.df_users[["id", "gender"]],
            left_on="client_id",
            right_on="id",
            how="left"
        )

        # Group & sum
        gender_sums = (
            df_merged
            .groupby("gender")["amount"]
            .sum()
            .to_dict()
        )

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

        # Copy & optional filter
        df = self.df_transactions.copy()
        if state:
            df = df[df["state_name"] == state]

        # Merge with user ages
        df_merged = pd.merge(
            df[["client_id", "amount"]],
            self.df_users[["id", "current_age"]],
            left_on="client_id",
            right_on="id",
            how="left"
        )

        # Create age groups like "20-30", "30-40", etc.
        df_merged["age_group"] = (
                df_merged["current_age"].floordiv(10).mul(10).astype(int).astype(str)
                + "-"
                + (df_merged["current_age"].floordiv(10).mul(10) + 10).astype(int).astype(str)
        )

        # Group by age group and sum amounts
        age_group_sums = (
            df_merged
            .groupby("age_group")["amount"]
            .sum()
            .sort_index()
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

        # Work on a copy
        df = self.df_transactions.copy()

        # Normalize use_chip for matching
        df["use_chip_norm"] = df["use_chip"].str.strip().str.lower()

        # All online transactions (state_name may be null)
        online_mask = df["use_chip_norm"].str.startswith("online")
        online_sum = df.loc[online_mask, "amount"].sum()

        # In-Store: only swipe transactions, optionally filtered by state
        instore_mask = df["use_chip_norm"].str.startswith("swipe")
        if state:
            instore_mask &= (df["state_name"] == state)
        instore_sum = df.loc[instore_mask, "amount"].sum()

        result = {
            "Online": online_sum,
            "In-Store": instore_sum
        }

        # Cache & return
        self._cache_expenditures_by_channel[state] = result
        return result

    # TODO: @SonPhạm: Tab User - User/Card KPIs

    def get_user_kpis(self, user_id: int) -> dict:
        """
        Gibt KPIs für einen bestimmten User zurück.
        Kreditlimit ist die SUMME aller Kreditlimits der Karten des Users.
        """
        tx = self.df_transactions[self.df_transactions["client_id"] == user_id]
        # user_row = self.df_users[self.df_users["id"] == user_id]  # credit_limit gibt es hier NICHT!
        card_count = self.df_cards[self.df_cards["client_id"] == user_id].shape[0]
        # Kreditlimit aller Karten summieren:
        cards = self.df_cards[self.df_cards["client_id"] == user_id]
        credit_limit = cards["credit_limit"].sum() if not cards.empty else None

        return {
            "amount_of_transactions": tx.shape[0],
            "total_sum": tx["amount"].sum(),
            "average_amount": tx["amount"].mean() if tx.shape[0] > 0 else 0,
            "amount_of_cards": card_count,
            "credit_limit": credit_limit
        }

    def get_card_kpis(self, card_id: int) -> dict:
        """
        Gibt KPIs für eine bestimmte Card zurück.
        """
        card_row = self.df_cards[self.df_cards["id"] == card_id]
        if card_row.empty:
            return {"amount_of_transactions": 0, "total_sum": 0, "average_amount": 0, "amount_of_cards": 0,
                    "credit_limit": None}
        user_id = card_row.iloc[0]["client_id"]
        d = self.get_user_kpis(user_id)
        # Card hat ggf. eigenes Kreditlimit, das überschreibt das des Users!
        credit_limit = float(card_row.iloc[0]["credit_limit"]) if not card_row.empty else d["credit_limit"]
        d["credit_limit"] = credit_limit
        return d

    def get_credit_limit(self, user_id: int = None, card_id: int = None):
        """
        Gibt das Kreditlimit zurück (Card hat Priorität).
        - Wenn Card-ID angegeben, zeige das Kreditlimit der Karte.
        - Wenn nur User-ID angegeben, aggregiere über alle Karten des Users (z.B. Summe).
        """
        if card_id is not None:
            card_row = self.df_cards[self.df_cards["id"] == card_id]
            if not card_row.empty:
                return card_row.iloc[0]["credit_limit"]

        if user_id is not None:
            user_cards = self.df_cards[self.df_cards["client_id"] == user_id]
            if not user_cards.empty:
                # Du kannst auch mean() oder sum() nehmen je nach gewünschter Logik!
                return user_cards["credit_limit"].sum()  # Summe aller Limits des Users
        return None

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
        # logger.log(f"ℹ️ Users: {self.units_users}", 2)
        # logger.log(f"ℹ️ Transactions: {self.units_transactions}", 2)
        # logger.log(f"ℹ️ Cards: {self.units_cards}", 2)
