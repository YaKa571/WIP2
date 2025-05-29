import json
from typing import Optional, List

import pandas as pd
from sklearn.cluster import KMeans

from utils import logger
from utils.benchmark import Benchmark


class ClusterTabData:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.df_transactions = data_manager.df_transactions
        self.df_users = data_manager.df_users
        
        # Initialize dataframes and data
        self.my_mcc = None
        self.my_data_file = None
        
        # Constants
        self.cluster_colors = {
            "0": "#56B4E9",  # light blue
            "1": "#D55E00",  # reddish brown
            "2": "#009E73",  # teal green
            "3": "#E69F00",  # orange
            "4": "#0072B2",  # dark blue
            "5": "#F0E442",  # yellow
            "6": "#CC79A7",  # pink/magenta
            "7": "#999999",  # grey
            "8": "#ADFF2F",  # light green
            "9": "#87CEEB"   # sky blue
        }
        
        # Age group bins and labels
        self.age_bins = [0, 25, 35, 45, 55, 65, 200]
        self.age_labels = ['<25', '26–35', '36–45', '46–55', '56–65', '65+']
        
        # Caches
        self._cache_cluster_data = {}
        self._cache_inc_vs_exp_cluster_data = {}
    
    def initialize(self):
        """
        Initialize the cluster tab data by loading and processing the necessary data.
        """
        logger.log("ℹ️ Initializing Cluster Tab Data...", 2)
        bm = Benchmark("Initialization")
        
        # Load MCC codes
        with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
        self.my_mcc["mcc"] = self.my_mcc["mcc"].astype(int)
        
        # Get transaction data from merchant tab data
        self.my_data_file = self.data_manager.merchant_tab_data.get_my_transactions_mcc_users()
        
        # Add age_group
        self.my_data_file['age_group'] = pd.cut(
            self.my_data_file['current_age'], 
            bins=self.age_bins, 
            labels=self.age_labels
        )
        
        bm.print_time(level=3)
    
    def get_cluster_merchant_group_dropdown(self) -> List[str]:
        """
        Generate a sorted list of unique merchant groups for a dropdown menu.

        Returns:
            list: Sorted list of merchant groups with 'All Merchant Groups' as the first option.
        """
        my_list = sorted(self.my_mcc['merchant_group'].unique().tolist())
        my_list.insert(0, 'All Merchant Groups')
        return my_list
    
    def get_cluster_colors(self) -> dict:
        """
        Get the color mapping for clusters.
        
        Returns:
            dict: A dictionary mapping cluster IDs to color codes.
        """
        return self.cluster_colors
    
    def prepare_cluster_data(self, merchant_group) -> pd.DataFrame:
        """
        Prepare and cluster transaction data based on transaction count and value.

        Args:
            merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

        Returns:
            pd.DataFrame: Aggregated data with cluster labels based on total and average transaction values.
        """
        # Check cache
        cache_key = f"cluster_data_{merchant_group}"
        if cache_key in self._cache_cluster_data:
            return self._cache_cluster_data[cache_key]
        
        # Get a copy of the data
        df = self.my_data_file.copy()
        
        # Optional: Merchant Group filter
        if merchant_group != 'All Merchant Groups':
            df = df[df['merchant_group'] == merchant_group].copy()

        df['age_group_plot'] = df['age_group']  # for plotting

        # Aggregation per client_id
        agg = df.groupby('client_id').agg(
            transaction_count=('amount', 'count'),
            total_value=('amount', 'sum'),
            age_group=('age_group_plot', 'first')  # one age group per client
        ).reset_index()

        agg['average_value'] = agg['total_value'] / agg['transaction_count']

        # Check the number of data points
        n_samples = len(agg)

        # Clustering 1: total_value vs count
        n_clusters_total = min(4, n_samples)
        if n_clusters_total >= 1:
            kmeans_total = KMeans(n_clusters=n_clusters_total, random_state=42, n_init=30)
            agg['cluster_total'] = kmeans_total.fit_predict(agg[['transaction_count', 'total_value']])
        else:
            agg['cluster_total'] = 0  # fallback for 0 rows
        agg['cluster_total_str'] = agg['cluster_total'].astype(str)

        # Clustering 2: average_value vs count
        n_clusters_avg = min(4, n_samples)
        if n_clusters_avg >= 1:
            kmeans_avg = KMeans(n_clusters=n_clusters_avg, random_state=42, n_init=30)
            agg['cluster_avg'] = kmeans_avg.fit_predict(agg[['transaction_count', 'average_value']])
        else:
            agg['cluster_avg'] = 0
        agg['cluster_avg_str'] = agg['cluster_avg'].astype(str)
        
        # Cache the result
        self._cache_cluster_data[cache_key] = agg
        
        return agg
    
    def prepare_inc_vs_exp_cluster_data(self, merchant_group) -> pd.DataFrame:
        """
        Prepare and cluster data based on yearly income versus total expenses.

        Args:
            merchant_group (str): Merchant group filter; if not 'All Merchant Groups', filter the data.

        Returns:
            pd.DataFrame: Aggregated data with clusters for income vs expenses.
        """
        # Check cache
        cache_key = f"inc_vs_exp_cluster_data_{merchant_group}"
        if cache_key in self._cache_inc_vs_exp_cluster_data:
            return self._cache_inc_vs_exp_cluster_data[cache_key]
        
        # Get a copy of the data
        df = self.my_data_file.copy()
        
        # Filtering
        if merchant_group != 'All Merchant Groups':
            df = df[df['merchant_group'] == merchant_group].copy()

        # Aggregation per client_id
        agg = df.groupby('client_id').agg(
            total_expenses=('amount', 'sum'),
            yearly_income=('yearly_income', 'first'),
            age_group=('age_group', 'first')
        ).reset_index()

        # drop NaNs
        agg = agg.dropna(subset=['total_expenses', 'yearly_income'])

        n_samples = len(agg)
        n_clusters = min(4, n_samples)

        if n_clusters >= 1:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=30)
            agg['cluster_inc_vs_exp'] = kmeans.fit_predict(agg[['yearly_income', 'total_expenses']])
        else:
            agg['cluster_inc_vs_exp'] = 0

        agg['cluster_inc_vs_exp_str'] = agg['cluster_inc_vs_exp'].astype(str)
        
        # Cache the result
        self._cache_inc_vs_exp_cluster_data[cache_key] = agg
        
        return agg
    
    def get_data_file(self) -> pd.DataFrame:
        """
        Get the processed data file with age groups.
        
        Returns:
            pd.DataFrame: The processed data file.
        """
        return self.my_data_file