from pathlib import Path
from typing import Optional

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
from utils.utils import rounded_rect

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

        self._cache_most_valuable_merchant: dict[str, pd.DataFrame] = {}
        self._cache_visits_by_merchant: dict[Optional[str], pd.DataFrame] = {}
        self._cache_spending_by_user: dict[Optional[str], pd.DataFrame] = {}
        self._cache_transaction_counts_by_hour: dict[Optional[str], pd.DataFrame] = {}
        self._cache_expenditures_by_gender: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_age: dict[str | None, dict[str, float]] = {}
        self._cache_expenditures_by_channel: dict[str | None, dict[str, float]] = {}

        self.online_shape = list[list]

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

            # Null value -> Online
            df["state_name"] = df["state_name"].fillna("ONLINE")

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

    def get_merchant_values_by_state(self, state: str = None) -> pd.DataFrame:
        """
        Fetches and processes merchant transaction data grouped by state and mcc.

        This method returns a DataFrame containing the aggregated transaction amount
        per merchant grouped by 'merchant_id' and 'mcc', sorted in descending order
        by total transaction amount. If a specific state is provided, the data is
        filtered for that state. Processed results are cached to enhance
        performance for repeated calls with the same state.

        Parameters:
        state: str, optional
            The state for which data needs to be fetched. If None, data for all states
            is processed.

        Returns:
        DataFrame
            A DataFrame containing the aggregated transaction amounts by
            'merchant_id' and 'mcc', sorted in descending order of the total
            transaction amount. Includes a column with MCC descriptions.

        Raises:
            KeyError: If the provided state doesn't exist in the transaction data.
        """
        if state in self._cache_most_valuable_merchant:
            return self._cache_most_valuable_merchant[state]

        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        df_sums = (
            df.groupby(["merchant_id", "mcc"])["amount"]
            .sum()
            .reset_index(name="merchant_sum")
            .sort_values("merchant_sum", ascending=False)
        )

        # Apply the same helper used in KPI to each MCC code.
        df_sums["mcc_desc"] = df_sums["mcc"].apply(
            lambda m: get_mcc_description_by_merchant_id(self.mcc_dict, int(m))
        )

        self._cache_most_valuable_merchant[state] = df_sums
        return df_sums

    def get_most_valuable_merchant(self, state: str = None) -> MerchantKPI:
        """
        Fetches the most valuable merchant based on the given state and associated metrics.

        This method determines the top-performing merchant by analyzing transaction data,
        and optionally filters the data by a specific state. It utilizes auxiliary methods
        to calculate the necessary metrics and retrieve MCC (Merchant Category Code)
        descriptions.

        Args:
            state (str, optional): A specific state used to filter merchant transaction
            data. Defaults to None.

        Returns:
            MerchantKPI: An object containing details about the most valuable merchant,
            including its ID, MCC, MCC description, and the total transaction value.
        """
        # Reuse get_merchant_values_by_state to avoid duplicate logic.
        df_sums = self.get_merchant_values_by_state(state)
        top = df_sums.iloc[0]

        return MerchantKPI(
            id=int(top["merchant_id"]),
            mcc=int(top["mcc"]),
            mcc_desc=get_mcc_description_by_merchant_id(self.mcc_dict, int(top["mcc"])),
            value=f"{float(top['merchant_sum']):,.2f}"
        )

    def get_transaction_counts_by_hour(self, state: str = None) -> pd.DataFrame:
        """
        Retrieves transaction counts grouped by hour with an optional state filter.

        This method calculates the number of transactions grouped by hour of the day.
        It can filter transactions by a specific state if provided. The results are
        sorted in descending order by transaction count. The computed results are
        also cached for efficiency.

        Parameters:
        state: str, optional
            The name of the state to filter transactions by. If None, transactions
            from all states are considered.

        Returns:
        pd.DataFrame
            A DataFrame containing two columns:
            - 'hour': The hour of the day (0-23).
            - 'transaction_count': The number of transactions that occurred in each
               hour, sorted in descending order.
        """
        # Cache-Check
        if state in self._cache_transaction_counts_by_hour:
            return self._cache_transaction_counts_by_hour[state]

        # Filter state
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Copy & Datetime -> extract hour
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["hour"] = df["date"].dt.hour

        # Group & count
        df_counts = (
            df.groupby("hour")
            .size()
            .reset_index(name="transaction_count")
        )

        # Sort descending by count
        df_counts = df_counts.sort_values("transaction_count", ascending=False)

        # Cache & return
        self._cache_transaction_counts_by_hour[state] = df_counts
        return df_counts

    def get_peak_hour(self, state: str = None) -> PeakHourKPI:
        """
        Determines the hour with the highest transaction activity and formats the data into
        a PeakHourKPI object. The method calculates the hourly transaction count for a given
        state, identifies the hour with the most activity, formats the hour range and count,
        and returns the information encapsulated in a KPI.

        Args:
        state (str, optional): The specific state to filter the transaction data. Defaults to
        None, indicating no state-based filtering.

        Returns:
        PeakHourKPI: An object representing the hour range with the highest transaction count
        and the formatted count value.
        """
        # Reuse the DataFrame-method
        df_counts = self.get_transaction_counts_by_hour(state)

        # Pick the top row
        top = df_counts.iloc[0]
        most_active_hour = int(top["hour"])
        count = int(top["transaction_count"])

        # Format hour range
        hour_str = f"{most_active_hour:02d}:00 – {(most_active_hour + 1) % 24:02d}:00"
        # Format value with thousands separator
        value_str = f"{count:,}".replace(",", ".")

        # Build and return KPI
        return PeakHourKPI(hour_range=hour_str, value=value_str)

    def get_spending_by_user(self, state: str = None) -> pd.DataFrame:
        """
        Computes the total spending by users filtered by an optional state, caches the result,
        and returns the data as a sorted DataFrame.

        Parameters
        ----------
        state : str, optional
            The name of the state to filter the transactions by. If None, all transaction
            data is considered.

        Returns
        -------
        pd.DataFrame
            A DataFrame with two columns: 'client_id' and 'spending', where 'spending'
            represents the total amount spent by each user. The DataFrame is sorted in
            descending order by 'spending'.
        """
        # Cache-Check
        if state in self._cache_spending_by_user:
            return self._cache_spending_by_user[state]

        # Filter data by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        # Sum spending per client
        df = df.copy()
        df_sums = (
            df.groupby("client_id")["amount"]
            .sum()
            .reset_index(name="spending")
        )

        # Sort by spending descending
        df_sums = df_sums.sort_values("spending", ascending=False)

        # Cache & return
        self._cache_spending_by_user[state] = df_sums
        return df_sums

    def get_top_spending_user(self, state: str = None) -> UserKPI:
        """
        Determines the top spending user for a given state or overall based on the
        highest spending. Retrieves additional user details to construct the result.

        Arguments:
        state: str or None
            Optional. Specifies the U.S. state for filtering. If None, considers all
            states.

        Returns:
        UserKPI
            An object containing details of the top spending user, including their
            ID, gender, current age, and the formatted spending value.
        """
        # Reuse DataFrame-method
        df_sums = self.get_spending_by_user(state)
        top = df_sums.iloc[0]
        client_id = int(top["client_id"])
        spending = float(top["spending"])

        # Lookup additional user details
        user_row = self.df_users.loc[self.df_users["id"] == client_id].iloc[0]
        gender = user_row["gender"]
        current_age = int(user_row["current_age"])

        # Format spending value
        value_str = f"{spending:,.2f}"

        return UserKPI(
            id=client_id,
            gender=gender,
            current_age=current_age,
            value=value_str
        )

    def get_visits_by_merchant(self, state: str = None) -> pd.DataFrame:
        """
        Retrieves the number of visits to merchants based on transaction data. Optionally filters
        the result by a specific state.

        Args:
            state (str, optional): The name of the state to filter transaction data by. If not
            provided, visits are calculated for all data. Default is None.

        Returns:
            pd.DataFrame: A DataFrame containing the number of visits to each merchant, along
            with the merchant category code (MCC) and its description.

        Raises:
            None
        """
        if state in self._cache_visits_by_merchant:
            return self._cache_visits_by_merchant[state]

        # Filter by state if provided
        df = self.df_transactions
        if state:
            df = df[df["state_name"] == state]

        df = df.copy()
        visit_counts = (
            df.groupby("merchant_id")["merchant_id"]
            .size()
            .reset_index(name="visits")
            .sort_values("visits", ascending=False)
        )
        # Lookup MCC and description
        visit_counts['mcc'] = visit_counts['merchant_id'].apply(
            lambda mid: int(df.loc[df['merchant_id'] == mid, 'mcc'].iloc[0])
        )
        visit_counts['mcc_desc'] = visit_counts['mcc'].apply(
            lambda m: get_mcc_description_by_merchant_id(self.mcc_dict, m)
        )

        self._cache_visits_by_merchant[state] = visit_counts
        return visit_counts

    def get_most_visited_merchant(self, state: str = None) -> VisitKPI:
        """
        Retrieves the most visited merchant data based on visit count. The merchant with the highest number of visits in the
        specified state is determined. The result includes merchant ID, MCC, MCC description, and formatted visit count.

        Args:
            state (str, optional): The state for which the most visited merchant should be retrieved. If not provided, the search
                                   will not be state-specific.

        Returns:
            VisitKPI: An object containing the most visited merchant's data including merchant ID, MCC, MCC description, and
                      formatted visit count.
        """
        df_visits = self.get_visits_by_merchant(state)
        top = df_visits.iloc[0]
        mid = int(top["merchant_id"])
        visits = int(top["visits"])
        mcc = int(top["mcc"])
        desc = top["mcc_desc"]

        visits_str = f"{visits:,}".replace(",", ".")
        return VisitKPI(id=mid, mcc=mcc, mcc_desc=desc, visits=visits_str)

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

        # Keys uppercased
        gender_sums = {str(k).upper(): v for k, v in gender_sums.items()}

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
        if state == "ONLINE":
            instore_sum = 0  # No In-store for Online Transactions
        else:
            instore_mask = df["use_chip_norm"].str.startswith("swipe")
            if state:
                instore_mask &= (df["state_name"] == state)
            instore_sum = df.loc[instore_mask, "amount"].sum()

        result = {
            "ONLINE": online_sum,
            "IN-STORE": instore_sum
        }

        # Cache & return
        self._cache_expenditures_by_channel[state] = result
        return result

    def _pre_cache_home_tab_data(self, log_state_times: bool = True) -> None:
        """
        Pre-caches data for the Home-Tab view by performing data aggregation and calculations for
        both overall data and state-specific data. This method is intended to optimize subsequent
        data retrieval and ensure that necessary insights are readily available for analysis. The
        method executes a series of predefined data aggregation functions for all states in the
        transaction dataset.

        Parameters
        ----------
        self : object
            An instance of the class for which the method is defined. It provides access
            to attributes and other methods of the object.

        Raises
        ------
        None

        Returns
        -------
        None
        """
        bm_pre_cache_full = Benchmark("Pre-caching Home-Tab data")
        logger.log("🔄 Pre-caching Home-Tab data...", indent_level=2)

        # First for overall (state=None)
        bm_usa_wide = Benchmark("Pre-caching of USA-wide data")
        self.get_merchant_values_by_state(state=None)
        self.get_transaction_counts_by_hour(state=None)
        self.get_spending_by_user(state=None)
        self.get_visits_by_merchant(state=None)
        self.get_expenditures_by_gender(state=None)
        self.get_expenditures_by_age(state=None)
        self.get_expenditures_by_channel(state=None)
        bm_usa_wide.print_time(level=3)

        # Then for each individual state
        states = self.df_transactions['state_name'].dropna().unique().tolist()
        counter = 1

        for st in states:
            bm_state = Benchmark("(" + str(counter) + ") Pre-caching of state " + st)
            self.get_merchant_values_by_state(state=st)
            self.get_transaction_counts_by_hour(state=st)
            self.get_spending_by_user(state=st)
            self.get_visits_by_merchant(state=st)
            self.get_expenditures_by_gender(state=st)
            self.get_expenditures_by_age(state=st)
            self.get_expenditures_by_channel(state=st)

            if log_state_times:
                bm_state.print_time(level=3)
                counter += 1

        bm_pre_cache_full.print_time(level=3)

    # TODO: @SonPhạm: Tab User - User/Card KPIs
    def get_user_kpis(self, user_id: int) -> dict:
        """
        Gibt KPIs für einen bestimmten User korrekt zurück.
        """
        # Stelle sicher, dass client_id als int verglichen wird!
        tx = self.df_transactions[self.df_transactions["client_id"].astype(int) == int(user_id)]
        cards_user = self.df_cards[self.df_cards["client_id"].astype(int) == int(user_id)]
        credit_limit = cards_user["credit_limit"].sum() if not cards_user.empty else 0

        return {
            "amount_of_transactions": tx.shape[0],
            "total_sum": tx["amount"].sum(),
            "average_amount": tx["amount"].mean() if tx.shape[0] > 0 else 0,
            "amount_of_cards": cards_user.shape[0],
            "credit_limit": credit_limit
        }

    def get_card_kpis(self, card_id: int) -> dict:
        """
        Gibt KPIs für eine bestimmte Karte (card_id) korrekt zurück.
        - Zeigt die KPIs für den Besitzer der Karte an.
        - Kreditlimit ist das der Karte.
        """
        # Finde die Karte
        card_row = self.df_cards[self.df_cards["id"] == card_id]
        if card_row.empty:
            return {
                "amount_of_transactions": 0,
                "total_sum": 0,
                "average_amount": 0,
                "amount_of_cards": 0,
                "credit_limit": None
            }
        user_id = card_row.iloc[0]["client_id"]

        # Hole die KPIs für diesen User
        data = self.get_user_kpis(user_id)

        # Überschreibe das Kreditlimit mit dem Limit der Karte!
        data["credit_limit"] = card_row.iloc[0]["credit_limit"]

        return data

    def get_credit_limit(self, user_id: int = None, card_id: int = None):
        """
        Gibt das Kreditlimit zurück (Card-ID hat Priorität).
        - Falls Card-ID angegeben, das Kreditlimit dieser Karte.
        - Falls nur User-ID, Summe der Kreditlimits aller Karten dieses Users.
        """
        if card_id is not None:
            card_row = self.df_cards[self.df_cards["id"] == card_id]
            if not card_row.empty:
                return float(card_row.iloc[0]["credit_limit"])
        if user_id is not None:
            user_cards = self.df_cards[self.df_cards["client_id"] == user_id]
            if not user_cards.empty:
                return float(user_cards["credit_limit"].sum())
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
                                                                                       num_rows=50_000))
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
        self._pre_cache_home_tab_data()
        self.online_shape = rounded_rect(
            l=-95, b=23, r=-85, t=28,
            radius=0.7,
            n_arc=8
        )

        # Print summary
        # logger.log(f"ℹ️ Users: {self.units_users}", 2)
        # logger.log(f"ℹ️ Transactions: {self.units_transactions}", 2)
        # logger.log(f"ℹ️ Cards: {self.units_cards}", 2)

# Test für Summe Transaktionen bei User-ID 123. Im Dashboard 463, aber Pycharm 27?

# print("Transaktionen für client_id 123:",
#      self.df_transactions[self.df_transactions["client_id"] == 123].shape[0])
# print("Typ von client_id in transactions:", self.df_transactions["client_id"].dtype)
# print("Alle Werte für client_id 123 (head):")
# print(self.df_transactions[self.df_transactions["client_id"] == 123].head())
