import pandas as pd

from backend.data_handler import get_mcc_description_by_merchant_id
from utils import logger
from utils.benchmark import Benchmark


class UserTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # Caches
        self._cache_user_transactions: dict[int, pd.DataFrame] = {}  # user_id -> DataFrame
        self._cache_user_merchant_agg: dict[int, pd.DataFrame] = {}  # user_id -> Aggregated DataFrame
        self.unique_user_ids = set(data_manager.df_users["id"].unique())
        self.unique_card_ids = set(data_manager.df_cards["id"].unique())

    def cache_user_transactions(self):
        """
        Caches user transactions by grouping them by client ID.

        This method processes the transactions DataFrame (df_transactions) by grouping
        transactions based on the "client_id" column. For each unique client ID, it
        creates a reference to the corresponding subset of the DataFrame and stores it in
        a dictionary. The dictionary is stored as an internal attribute
        (_cache_user_transactions), where the keys represent client IDs and the values
        are the dataframes containing transactions for each user.

        Raises:
            KeyError: If the DataFrame does not contain a "client_id" column.
            AttributeError: If df_transactions is not a valid DataFrame object.
        """
        # Use a more memory-efficient approach by storing references instead of copies
        # Only create copies when the dataframe is actually modified
        self._cache_user_transactions = {}

        # Convert client_id to int once to avoid repeated conversions
        df = self.data_manager.df_transactions.copy()
        if not pd.api.types.is_integer_dtype(df['client_id']):
            df['client_id'] = df['client_id'].astype(int)

        # Group by client_id and store references to the groups
        for user_id, group in df.groupby("client_id"):
            self._cache_user_transactions[int(user_id)] = group

    def cache_user_merchant_agg(self):
        """
        Caches aggregated user merchant data.

        This method processes user transaction data to calculate and cache aggregated
        information by merchant and MCC (Merchant Category Code) for each user. It
        groups the data by merchant ID and MCC, computes the total transaction count
        and sum of amounts for each group, adds merchant category descriptions, and
        stores the results in a dictionary.

        Attributes:
            _cache_user_merchant_agg (dict[int, DataFrame]): A dictionary mapping user
            IDs (int) to their corresponding aggregated transaction data (DataFrame).
            Each DataFrame contains the merchant ID, MCC, transaction count, total
            transaction amount, and merchant category description for the user.

        Raises:
            KeyError: Raised if certain keys or values are not present in the input
            data or dictionaries during processing.

        """
        # Pre-create the dictionary to avoid resizing
        self._cache_user_merchant_agg = {}

        # Create a mapping of MCC codes to descriptions once instead of repeatedly calling the function
        df_mcc = self.data_manager.df_mcc
        unique_mccs = set()

        # First collect all unique MCCs
        for _, df_tx in self._cache_user_transactions.items():
            if 'mcc' in df_tx.columns:
                unique_mccs.update(df_tx['mcc'].unique())

        # Create the mapping dictionary
        mcc_to_desc = {
            int(mcc): get_mcc_description_by_merchant_id(df_mcc, int(mcc))
            for mcc in unique_mccs if pd.notna(mcc)
        }

        # Process each user's transactions
        for user_id, df_tx in self._cache_user_transactions.items():
            # Skip if dataframe is empty
            if df_tx.empty:
                continue

            # Perform aggregation
            agg = df_tx.groupby(["merchant_id", "mcc"]).agg(
                tx_count=("amount", "size"),
                total_sum=("amount", "sum")
            ).reset_index()

            # Skip if aggregation is empty
            if agg.empty:
                continue

            # Add MCC description using the pre-computed mapping
            # Convert MCC to int once for the whole column
            if not pd.api.types.is_integer_dtype(agg['mcc']):
                agg['mcc'] = agg['mcc'].astype(int)

            # Use vectorized mapping instead of apply with lambda
            agg["mcc_desc"] = agg["mcc"].map(mcc_to_desc)

            # Filter out rows with tx_count == 0 or total_sum == 0
            # This is more efficient than filtering after the fact
            mask = (agg["tx_count"] != 0) & (agg["total_sum"] != 0)
            if not mask.all():
                agg = agg[mask]

            self._cache_user_merchant_agg[int(user_id)] = agg

    def get_user_kpis(self, user_id: int) -> dict:
        """
        Returns key performance indicators (KPIs) of a specified user based
        on their transactions and card information. This method calculates
        details like the number of transactions, total transaction sum,
        average transaction amount, the number of cards owned, and the
        sum of credit limits available to the user.

        Args:
            user_id (int): The unique identifier of the user for whom to
                calculate the KPIs.

        Returns:
            dict: A dictionary containing the following KPIs:
                - "amount_of_transactions" (int): The total number of
                  transactions made by the user.
                - "total_sum" (float): The sum of all transaction amounts
                  related to the user.
                - "average_amount" (float): The average value of the user's
                  transactions, or 0 if no transactions exist.
                - "amount_of_cards" (int): The total number of cards the user
                  owns.
                - "credit_limit" (float): The combined credit limit from all
                  cards the user possesses.
        """
        # Make sure to compare client_id as int
        tx = self.data_manager.df_transactions[
            self.data_manager.df_transactions["client_id"].astype(int) == int(user_id)]
        cards_user = self.data_manager.df_cards[self.data_manager.df_cards["client_id"].astype(int) == int(user_id)]
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
        Provides KPIs for a specific card, including transaction details and card credit limit.

        Parameters
        ----------
        card_id : int
            The unique identifier of the card.

        Returns
        -------
        dict
            A dictionary containing the following key-value pairs:
                - amount_of_transactions (int): Number of transactions associated with
                  the card.
                - total_sum (int): Total sum of all transactions related to the card.
                - average_amount (int): Average transaction amount for the card.
                - amount_of_cards (int): Total number of active cards associated with
                  the same user as the specified card.
                - credit_limit (Optional[int]): The credit limit of the given card. It
                  is set to None if the specified card does not exist.
        """
        # Find the card
        card_row = self.data_manager.df_cards[self.data_manager.df_cards["id"] == card_id]
        if card_row.empty:
            return {
                "amount_of_transactions": 0,
                "total_sum": 0,
                "average_amount": 0,
                "amount_of_cards": 0,
                "credit_limit": None
            }
        user_id = card_row.iloc[0]["client_id"]

        # Get the card for that user
        data = self.get_user_kpis(user_id)

        # Overwrite credit limit with card's credit limit
        data["credit_limit"] = card_row.iloc[0]["credit_limit"]

        return data

    def get_credit_limit(self, user_id: int = None, card_id: int = None):
        """
        Retrieve the credit limit for a specific user or card.

        This method determines the credit limit by checking the provided user
        or card ID. If a card ID is given, it retrieves the credit limit for
        that specific card. If a user ID is given, it calculates the total
        credit limit for all cards associated with the user. If neither user
        ID nor card ID is provided, or no information is found, the method
        returns None.

        Args:
            user_id: int, optional
                The ID of the user whose credit limit should be calculated.
            card_id: int, optional
                The ID of the card whose credit limit should be retrieved.

        Returns:
            float or None:
                Returns the credit limit as a floating-point number if found,
                otherwise None.
        """
        if card_id is not None:
            card_row = self.data_manager.df_cards[self.data_manager.df_cards["id"] == card_id]
            if not card_row.empty:
                return float(card_row.iloc[0]["credit_limit"])
        if user_id is not None:
            user_cards = self.data_manager.df_cards[self.data_manager.df_cards["client_id"] == user_id]
            if not user_cards.empty:
                return float(user_cards["credit_limit"].sum())
        return None

    def get_user_transactions(self, user_id: int) -> pd.DataFrame:
        """
        Retrieves the transactions associated with a specific user from the cache.

        This method accesses a cached record of user transactions and retrieves the
        transactions for the given user ID. If no transactions are found for the
        specified user ID, it returns an empty DataFrame.

        Args:
            user_id: The unique identifier of the user whose transactions are
                to be retrieved.

        Returns:
            A DataFrame containing the transactions associated with the given
            user ID. If no transactions exist for the user, an empty DataFrame
            is returned.
        """
        return self._cache_user_transactions.get(int(user_id), pd.DataFrame())

    def get_user_merchant_agg(self, user_id: int) -> pd.DataFrame:
        """
        Retrieve aggregated merchant data for a specific user from cache.

        This method fetches pre-aggregated merchant-level data for a given user from
        the cache. If no data is found for the user in the cache, it returns an empty
        pandas DataFrame. This function is useful for retrieving cached user-specific
        data quickly.

        Args:
            user_id (int): The ID of the user whose merchant aggregated data is to
            be retrieved.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the cached aggregated merchant
            data for the specified user. Returns an empty DataFrame if no data is
            cached for the given user.
        """
        return self._cache_user_merchant_agg.get(int(user_id), pd.DataFrame())

    def initialize(self):
        logger.log("🔄 User: Pre-caching User-Tab data...", indent_level=3, add_line_before=True)
        bm_pre_cache_full = Benchmark("User: Pre-caching User-Tab data")

        self.cache_user_transactions()
        self.cache_user_merchant_agg()
        bm_pre_cache_full.print_time(level=4, add_empty_line=True)
