class FraudTabData:
    def __init__(self, data_manager):
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
        """Returns a DataFrame with all fraud transactions."""
        if self._cache_fraud_cases is not None:
            return self._cache_fraud_cases
        df = self.df_transactions
        df_fraud = df[df["errors"].notnull() & (df["errors"] != "")]
        self._cache_fraud_cases = df_fraud
        return df_fraud

    def get_fraud_by_state(self):
        """Returns a DataFrame with fraud transaction counts by state."""
        if self._cache_fraud_by_state is not None:
            return self._cache_fraud_by_state
        df_fraud = self.get_fraud_cases()
        state_counts = df_fraud['merchant_state'].value_counts().reset_index()
        state_counts.columns = ['merchant_state', 'transaction_count']
        self._cache_fraud_by_state = state_counts
        return state_counts

    def get_online_transaction_share(self):
        """Returns a DataFrame with online/in-store fraud transaction share."""
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
        """Returns a DataFrame with the top 10 online merchants by fraud transaction count."""
        if self._cache_top_online_merchants is not None:
            return self._cache_top_online_merchants
        df_fraud = self.get_fraud_cases()
        online_df = df_fraud[df_fraud['merchant_city'].isna() | (df_fraud['merchant_city'].str.lower() == 'online')]
        top_merchants = online_df['merchant_id'].value_counts().nlargest(10).reset_index()
        top_merchants.columns = ['merchant_id', 'transaction_count']
        self._cache_top_online_merchants = top_merchants
        return top_merchants

    def get_fraud_by_age(self):
        """Returns a DataFrame with fraud transaction counts by age group."""
        df_fraud = self.get_fraud_cases()
        merged = df_fraud.merge(self.df_users, left_on="client_id", right_on="id", how="left")
        age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
        age_labels = ['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        merged['age_group'] = pd.cut(merged['age'], bins=age_bins, labels=age_labels, right=False)
        age_group_counts = merged['age_group'].value_counts().reset_index()
        age_group_counts.columns = ['age_group', 'transaction_count']
        return age_group_counts

    def initialize(self):
        """Preloads and caches all fraud tab data."""
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
        cache_data = {
            "fraud_by_state": self._cache_fraud_by_state,
            "online_share": self._cache_online_share,
            "top_online_merchants": self._cache_top_online_merchants,
        }
        self.data_manager.save_cache_to_disk("fraud_tab_caches", cache_data)

    def _load_caches_from_disk(self):
        cache_data = self.data_manager.load_cache_from_disk("fraud_tab_caches", is_dataframe=False)
        if cache_data is not None:
            self._cache_fraud_by_state = cache_data.get("fraud_by_state")
            self._cache_online_share = cache_data.get("online_share")
            self._cache_top_online_merchants = cache_data.get("top_online_merchants")
            return True
        return False