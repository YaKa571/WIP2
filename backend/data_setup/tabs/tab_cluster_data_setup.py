import json
import pandas as pd
import datetime
from sklearn.cluster import KMeans
from backend.data_setup.tabs.tab_merchant_data_setup import get_my_transactions_mcc_users
"""
contains data setup for Cluster tab
"""
# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
my_mcc["mcc"] = my_mcc["mcc"].astype(int)

my_data_file = get_my_transactions_mcc_users()
print(my_data_file.head())
def get_cluster_merchant_group_dropdown():
    my_df = my_mcc
    my_list = sorted(my_df['merchant_group'].unique().tolist())
    my_list.insert(0, 'All Merchant Groups')
    return my_list
