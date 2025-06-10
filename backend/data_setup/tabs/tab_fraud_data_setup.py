import pandas as pd

from utils import logger
from utils.benchmark import Benchmark


class FraudTabData:
    def __init__(self, data_manager):
        """
        Initializes the class with data_manager object and initializes its associated
        data frames and cache variables.

        Args:
            data_manager: An object that contains and manages the data frames
                df_transactions, df_users, and df_cards.

        Attributes:
            data_manager: The input data_manager object.
            df_transactions: Data frame containing transaction data, initialized
                from data_manager.
            df_users: Data frame containing user data, initialized from
                data_manager.
            df_cards: Data frame containing card data, initialized from
                data_manager.

            _cache_fraud_by_state: Cache for storing calculated fraud data grouped
                by state. Initialized to None.
            _cache_online_share: Cache for storing calculated share of online
                transactions. Initialized to None.
            _cache_top_online_merchants: Cache for storing top online merchants.
                Initialized to None.
            _cache_fraud_cases: Cache for storing fraud cases data. Initialized to
                None.
        """
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users
        self.df_cards = data_manager.df_cards

        # Caches
        self._cache_fraud_by_state = None
        self._cache_online_share = None
        self._cache_top_online_merchants = None
        self._cache_fraud_cases = None

    def get_fraud_cases(self):
        """
        Retrieves and caches fraud cases from the transactions dataframe.

        This method identifies rows in the transactions dataframe that are considered
        fraudulent based on the presence of non-null and non-empty values in the
        "errors" column. If the fraud cases have already been cached, it returns the
        cached data instead of re-computing.

        Returns:
            pd.DataFrame: A dataframe containing the rows from the transactions dataframe
            that are flagged as fraudulent based on the criteria.

        Attributes:
            df_transactions (pd.DataFrame): The original dataframe of transactions
            which is filtered to detect fraudulent entries.
            _cache_fraud_cases (Optional[pd.DataFrame]): An optional cached dataframe
            that stores previously computed fraudulent cases to avoid redundant
            computations.
        """
        if self._cache_fraud_cases is not None:
            return self._cache_fraud_cases
        df = self.df_transactions
        df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
        self._cache_fraud_cases = df_fraud
        return df_fraud

    def get_fraud_by_state(self):
        """
        Retrieves and caches the count of fraudulent transactions by state.

        This method calculates the number of fraudulent transactions grouped by merchant state
        using the internal fraud case data. The result is cached after the first computation
        for subsequent calls to avoid redundant computations.

        Args:
            None

        Returns:
            pandas.DataFrame: A DataFrame with two columns:
                - 'merchant_state': The state associated with the merchant.
                - 'transaction_count': The count of fraudulent transactions in that state.
        """
        if self._cache_fraud_by_state is not None:
            return self._cache_fraud_by_state
        df_fraud = self.get_fraud_cases()
        state_counts = df_fraud['merchant_state'].value_counts().reset_index()
        state_counts.columns = ['merchant_state', 'transaction_count']
        self._cache_fraud_by_state = state_counts
        return state_counts

    def get_online_transaction_share(self):
        """
        Calculates and returns the share of online transactions by analyzing fraud case data.

        This method determines whether each transaction is online or in-store based on the
        absence of merchant city information or if the merchant city is explicitly labeled
        as 'online'. The results, categorized as 'Online' or 'In-store', are then cached
        for reuse to optimize performance and avoid redundant calculations. If the result
        is already cached, it directly returns the cached value.

        Returns:
            pd.DataFrame: A DataFrame with two columns: 'type', which specifies the
            transaction type ('Online' or 'In-store'), and 'count', which represents
            the count of transactions for each type.
        """
        if self._cache_online_share is not None:
            return self._cache_online_share
        df_fraud = self.get_fraud_cases()
        df_fraud = df_fraud.copy()
        df_fraud['is_online'] = df_fraud['merchant_city'].isna() | (df_fraud['merchant_city'].str.lower() == 'online')
        counts = df_fraud['is_online'].value_counts().rename({True: 'Online', False: 'In-store'}).reset_index()
        counts.columns = ['type', 'count']
        self._cache_online_share = counts
        return counts

    def get_top_online_merchants(self):
        """
        Retrieves the top online merchants based on the number of transactions in fraud cases.

        This method filters fraud cases with missing or 'online'-labeled merchant cities. It then
        calculates the transaction counts for each online merchant and identifies the top ten
        merchants with the highest transaction counts. The result is cached for future calls
        to optimize performance.

        Returns:
            pandas.DataFrame: A DataFrame containing the top online merchants and their respective
            transaction counts. The DataFrame has two columns:
                - merchant_id: The identifier of the merchant.
                - transaction_count: The number of transactions associated with the merchant.
        """
        if self._cache_top_online_merchants is not None:
            return self._cache_top_online_merchants
        df_fraud = self.get_fraud_cases()
        online_df = df_fraud[df_fraud['merchant_city'].isna() | (df_fraud['merchant_city'].str.lower() == 'online')]
        top_merchants = online_df['merchant_id'].value_counts().nlargest(10).reset_index()
        top_merchants.columns = ['merchant_id', 'transaction_count']
        self._cache_top_online_merchants = top_merchants
        return top_merchants

    def get_fraud_by_age(self):
        """
        Analyzes fraudulent transactions by age group and returns the count of fraudulent
        transactions in each age category.

        This method retrieves fraudulent transaction data, merges it with user data to
        include age information, categorizes users into distinct age groups, and calculates
        the number of fraudulent transactions for each age group.

        Args:
            None

        Returns:
            pd.DataFrame: A DataFrame containing the age groups and corresponding counts of
            fraudulent transactions. The DataFrame has two columns:
                - 'age_group': The labels for age group categories (e.g., '<18', '18-24', etc.).
                - 'transaction_count': The number of fraudulent transactions in each age group.
        """
        df_fraud = self.get_fraud_cases()
        merged = df_fraud.merge(self.df_users, left_on="client_id", right_on="id", how="left")
        age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
        age_labels = ['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        merged['age_group'] = pd.cut(merged['age'], bins=age_bins, labels=age_labels, right=False)
        age_group_counts = merged['age_group'].value_counts().reset_index()
        age_group_counts.columns = ['age_group', 'transaction_count']
        return age_group_counts

    def initialize(self):
        """
        Initializes and prepares data for the Fraud Tab by loading caches from disk if available or calculating
        necessary data through various methods and storing the results to disk. The operation includes measuring
        execution time for performance analysis.

        Raises:
            Any exception that can be raised by associated methods or file operations such as cache loading
            and saving.

        """
        logger.log("ℹ️ Fraud: Initializing Fraud Tab Data...", 3, add_line_before=True)
        bm = Benchmark("Fraud: Initialization")
        if self._load_caches_from_disk():
            logger.log("✅ Fraud: Successfully loaded caches from disk", indent_level=3)
            bm.print_time(level=4, add_empty_line=True)
            return
        self.get_fraud_by_state()
        self.get_online_transaction_share()
        self.get_top_online_merchants()
        self.get_fraud_by_age()
        self._save_caches_to_disk()
        bm.print_time(level=4, add_empty_line=True)

    def _save_caches_to_disk(self):
        """
        Saves the current cache data to disk for persistent storage.

        This method organizes the cache data into a single dictionary and utilizes
        the `data_manager` to store the data under a specified key. It is used to
        ensure that the cached information remains available even after the process
        restarts.

        Args:
            None

        Returns:
            None
        """
        cache_data = {
            "fraud_by_state": self._cache_fraud_by_state,
            "online_share": self._cache_online_share,
            "top_online_merchants": self._cache_top_online_merchants,
        }
        self.data_manager.save_cache_to_disk("fraud_tab_caches", cache_data)

    def _load_caches_from_disk(self):
        """
        Loads cached data related to fraud and online activity from disk and assigns
        it to corresponding attributes. If no cache data is found, the attributes remain
        unchanged and the method returns False.

        Returns:
            bool: True if cache data is successfully loaded and assigned, otherwise False.
        """
        cache_data = self.data_manager.load_cache_from_disk("fraud_tab_caches", is_dataframe=False)
        if cache_data is not None:
            self._cache_fraud_by_state = cache_data.get("fraud_by_state")
            self._cache_online_share = cache_data.get("online_share")
            self._cache_top_online_merchants = cache_data.get("top_online_merchants")
            return True
        return False